const { ytdown } = require('priyansh-all-dl');
const axios = require('axios');
const fs = require('fs');
const path = require('path');

async function download() {
    const args = process.argv.slice(2);
    const url = args[0];
    const type = args[1]; // 'audio' or 'video'
    const outputPath = args[2];

    try {
        console.log(`Fetching data for URL: ${url}`);
        const data = await ytdown(url);
        
        if (!data || !data.data) {
            console.error('API Error: No data returned from ytdown');
            process.exit(1);
        }

        console.log('API Response received');
        let downloadUrl = '';
        
        if (type === 'audio') {
            downloadUrl = data.data.audio;
        } else {
            downloadUrl = data.data.video;
        }

        if (!downloadUrl) {
            console.error(`Error: No ${type} URL found in API response`);
            process.exit(1);
        }

        console.log(`Downloading from: ${downloadUrl}`);
        const response = await axios({
            method: 'GET',
            url: downloadUrl,
            responseType: 'stream',
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        });

        const writer = fs.createWriteStream(outputPath);
        response.data.pipe(writer);

        writer.on('finish', () => {
            console.log('Success');
            process.exit(0);
        });

        writer.on('error', (err) => {
            console.error('Writer error:', err.message);
            process.exit(1);
        });

    } catch (error) {
        console.error('Error:', error.message);
        process.exit(1);
    }
}

download();
