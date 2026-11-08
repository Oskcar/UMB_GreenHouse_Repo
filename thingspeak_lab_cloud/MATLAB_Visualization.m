channelID = 3521801;
readKey = '7XTP9UPM5EMVD0IW';

data = thingSpeakRead(channelID, 'NumPoints', 100, 'Location', true, ...
'ReadKey', readKey, 'OutputFormat', 'timetable');

% 1. Keep only rows that have a location
hasLocation = ~isnan(data.Latitude) & ~isnan(data.Longitude);
data = data(hasLocation, :);

if isempty(data)
title('No readings with a location yet');
return
end

% 2. Prepare one map we can draw on several times
gx = geoaxes;
hold(gx, 'on')

% 3. Draw each node once, using its newest row
nodeIDs = unique(data.node_id);
for k = 1:numel(nodeIDs)
rows = data(data.node_id == nodeIDs(k), :);
latest = rows(end, :);

geoscatter(gx, latest.Latitude, latest.Longitude, 120, 'filled');
text(gx, latest.Latitude, latest.Longitude, ...
sprintf(' Node %d: %.1f°C, %.0f%%', nodeIDs(k), latest.temperature, latest.humidity));
end

% 4. Finish the map
hold(gx, 'off')
geobasemap(gx, 'streets')
lastUpdate = data.Properties.RowTimes(end);
title(gx, sprintf('Latest reading per node (updated %s)', string(lastUpdate)))
