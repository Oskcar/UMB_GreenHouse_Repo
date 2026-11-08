channelID = 3521801;
readKey = "7XTP9UPM5EMVD0IW"

OFFLINE_MINUTES = 30; %How long before telling a node has gone offline
NUM_POINTS = 300; %rows received per hour + safety threshold ~ 80mins
EXPECTED_NODES = [1 2 3 4]; % every node that SHOULD be reporting

data = thingSpeakRead(channelID, 'NumPoints', NUM_POINTS, 'Location', true, ...
'ReadKey', readKey, 'OutputFormat', 'timetable');

t = data.Properties.RowTimes;
t.TimeZone = 'UTC';
data.Properties.RowTimes = t;

nowTime = datetime('now', 'TimeZone', 'UTC');

for k = 1:numel(EXPECTED_NODES)
id = EXPECTED_NODES(k);
rows = data(data.node_id == id, :);

if isempty(rows)
fprintf('Node %d: no readings in the last %d rows -> OFFLINE (no recent data)\n', ...
id, NUM_POINTS);
continue
end

latest = rows(end, :);
ageMinutes = minutes(nowTime - latest.Properties.RowTimes);

if ageMinutes > OFFLINE_MINUTES
status = 'OFFLINE?';
else
status = 'ok';
end

fprintf('Node %d: %.1f minutes old -> %s\n', id, ageMinutes, status);
end
