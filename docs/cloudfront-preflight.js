// Attach only to the nigiwai-topo/* behavior, viewer-request event.
function handler(event) {
    var request = event.request;
    if (request.method === 'OPTIONS') {
        return {
            statusCode: 204,
            statusDescription: 'No Content',
            headers: {
                'access-control-allow-origin': {value: '*'},
                'access-control-allow-methods': {value: 'GET, HEAD, OPTIONS'},
                'access-control-allow-headers': {value: 'Range, If-Match'},
                'access-control-max-age': {value: '3000'}
            }
        };
    }
    return request;
}
