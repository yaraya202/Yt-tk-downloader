import { YouTubeMusic } from '@mks2508/yt-dl';
import fs from 'fs';
import path from 'path';

async function download() {
    const args = process.argv.slice(2);
    const url = args[0];
    const type = args[1]; // 'audio' or 'video'
    const outputPath = args[2];

    try {
        console.log(`Fetching data for URL: ${url} (Type: ${type})`);
        
        let result;
        if (type === 'audio') {
            console.log('Downloading best audio...');
            result = await YouTubeMusic.downloadBestAudio(url, path.dirname(outputPath));
        } else {
            console.log('Downloading best video...');
            result = await YouTubeMusic.downloadBestCombined(url, path.dirname(outputPath));
        }

        if (result.success) {
            const downloadedFile = result.data.filePath;
            if (path.resolve(downloadedFile) !== path.resolve(outputPath)) {
                fs.renameSync(downloadedFile, outputPath);
            }
            console.log('Success');
            process.exit(0);
        } else {
            console.error('Download failed:', result.error);
            process.exit(1);
        }

    } catch (error) {
        console.error('Error:', error.message);
        process.exit(1);
    }
}

download();
