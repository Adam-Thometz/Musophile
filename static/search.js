const $searchWrapper = $('#searchWrapper');
const $searchType = $('#searchType');
const $searchBar = $('#searchBar');
const $searchResults = $('#searchResults');

const $limit = $('#limit')
const $searchBtn = $('#searchBtn')

const $displaySearch = $('.display-search');

const $addSong = $('.add-song')
const $accessToken = $('#accessToken')

accessToken = $accessToken.text()
localStorage.setItem('access_token', accessToken)

const MUSICBRAINZ_API_URL = 'https://musicbrainz.org/ws/2';
const SPOTIFY_API_URL = 'https://api.spotify.com/v1/search/'
// The MusicBrainz API returns a JSON response if you put the following string at the end of the request URL:
const JSON_FMT = 'fmt=json';

async function displayResults() {
    console.dir('displayResults')
    $searchResults.empty()
    const attr = $searchType.val();
    const term = $searchBar.val();
    const limit = $limit.val()
    const results = await getResults(attr, term, limit);

    for (let result of results) {
        const html = await generateResponseHTML(result)
        console.log(html)
        $searchResults.append(html)
    }
}

async function getResults(attr, term, limit) {
    console.dir('getResults')
    let resp;
    if (attr == 'recording'){
        resp = await axios.get(`${MUSICBRAINZ_API_URL}/${attr}/?query=${term}&limit=${limit}&${JSON_FMT}`)
    } else {
        resp = await axios.get(`${MUSICBRAINZ_API_URL}/recording/?query=${attr}:${term}&limit=${limit}&${JSON_FMT}`)
    }
    console.log(resp.data['recordings'])
    return resp.data['recordings']
}

async function generateResponseHTML(result) {
    console.dir('generateResponseHTML')
    const id = result["id"]
    const title = result['title']
    const artist = result['artist-credit'][0]['name']
    const release = result['releases'] ? result['releases'][0]['title'] : '<b>N/A</b>'
    const tags = result['tags'] ? result['tags'].map(tag => tag['name']) : 'N/A'

    let html = `<div class="search-result">
    <div class='result-info'>
        <ul>
            <li>Title: ${title}</li>
            <li>Artist: ${artist}</li>
            <li>Release: ${release}</li>
            <li>Tags: ${tags}</li>
        </ul>
    </div>`

    const spotify_player = await getSpotifyURIAndHTML(title, artist, id)
    html += spotify_player

    return html;
}

$searchBtn.click(displayResults)

async function getSpotifyURIAndHTML(title, artist, id) {
    console.dir('getSpotifyURIAndHTML')
    resp = await axios.get(`${SPOTIFY_API_URL}`, {
        params: {
            'q': `${title} ${artist}`,
            'type': 'track',
            'limit': 1
        }, 
        headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
        }
    })
    if (resp.data['tracks']['items'].length > 0){
        uri = resp.data['tracks']['items'][0]['uri'].slice(14)
        return `<div class="player">
                <iframe src="https://open.spotify.com/embed/track/${uri}" width="100%" height="80" frameBorder="0" allowtransparency="true" allow="encrypted-media"></iframe>
            </div>
            <aside class="search-result-options">
                <form action="/user/add-recording/${id}/${uri}" method="POST">
                    <button class='add-song'>Add to library</button>
                </form>
            </aside>
        </div>`
    } else {
        return `<aside class="search-result-options">
                <form action="/user/add-recording/${id}/0" method="POST">
                    <button class='add-song'>Add to library</button>
                </form>
            </aside>
        </div>`
    }
}