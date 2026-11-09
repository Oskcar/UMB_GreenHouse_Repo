% ---------- Settings ----------
DATA_CHANNEL = 3521801 ; % your sensor channel
DATA_READ_KEY = '7XTP9UPM5EMVD0IW';

EVENT_CHANNEL = 3521881; % your new Node Events channel
EVENT_READ_KEY = 'N7A7X3QRFFNCFTOH';
EVENT_WRITE_KEY = 'ELHCT30ANPLON3CN';

OFFLINE_MINUTES = 5; % testing: 5, not 2 (nodes report every ~70 s). Real value: 30

% ---------- 1. What is the status NOW? ----------
data = thingSpeakRead(DATA_CHANNEL, 'NumPoints', NUM_POINTS, 'Location', true, ...
'ReadKey', DATA_READ_KEY, 'OutputFormat', 'timetable');
t = data.Properties.RowTimes;
t.TimeZone = 'UTC';
data.Properties.RowTimes = t;
data = data(~isnan(data.Latitude) & ~isnan(data.Longitude), :);
nowTime = datetime('now', 'TimeZone', 'UTC');

% ---------- 2. What did we LAST LOG? ----------
eventLog = thingSpeakRead(EVENT_CHANNEL, 'NumPoints', 100, ...
'ReadKey', EVENT_READ_KEY, 'OutputFormat', 'timetable');

% ---------- 3. Check every node and COLLECT the changes ----------
changedIds = [];
changedLastRow = [];
changedCode = [];
changedLat = [];
changedLon = [];
changedSeen = [];

for k = 1:numel(EXPECTED_NODES)
id = EXPECTED_NODES(k);

% Status now, including the age so we can see the evidence
rows = data(data.node_id == id, :);
hasLatest = ~isempty(rows);
if hasLatest
latest = rows(end, :);
ageMinutes = minutes(nowTime - latest.Properties.RowTimes);
isOffline = ageMinutes > OFFLINE_MINUTES;
ageText = sprintf('%.1f min old', ageMinutes);
else
isOffline = true;
ageText = 'no recent data';
end

% Status last logged, and WHERE in the log (0 = never logged)
wasOffline = false;
lastRow = 0;
if ~isempty(eventLog)
idx = find(eventLog.node_id == id);
if ~isempty(idx)
lastRow = idx(end);
wasOffline = eventLog.event(lastRow) == EVENT_OFFLINE;
end
end

if isOffline == wasOffline
fprintf('Node %d (%s): no change (still %s)\n', id, ageText, statusText(isOffline));
elseif ~hasLatest
fprintf('Node %d (%s): offline, but no location to log\n', id, ageText);
else
fprintf('Node %d (%s): changed to %s\n', id, ageText, statusText(isOffline));
if isOffline
code = EVENT_OFFLINE;
else
code = EVENT_ONLINE;
end
changedIds(end + 1) = id;
changedLastRow(end + 1) = lastRow;
changedCode(end + 1) = code;
changedLat(end + 1) = latest.Latitude;
changedLon(end + 1) = latest.Longitude;
changedSeen(end + 1) = posixtime(latest.Properties.RowTimes);
end
end

% ---------- 4. Log ONE change: the node that has waited longest ----------
if ~isempty(changedIds)
[~, pick] = min(changedLastRow);
thingSpeakWrite(EVENT_CHANNEL, [changedIds(pick), changedCode(pick), changedSeen(pick)], ...
'WriteKey', EVENT_WRITE_KEY, ...
'Location', [changedLat(pick), changedLon(pick), 0]);
fprintf('-> LOGGED node %d. %d other change(s) will be logged on later runs.\n', ...
changedIds(pick), numel(changedIds) - 1);
end

function text = statusText(isOffline)
if isOffline
text = 'OFFLINE';
else
text = 'online';
end
end
