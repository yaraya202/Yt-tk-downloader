import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import fs from 'fs';

const execPromise = promisify(exec);

const COOKIES = process.env.YT_COOKIES || "";

async function download() {
    const args = process.argv.slice(2);
    const url = args[0];
    const type = args[1]; // 'audio' or 'video'
    const outputPath = args[2];

    try {
        console.log(`Fetching data for URL: ${url} (Type: ${type})`);
        
        // Get title first
        const titleResult = await execPromise(`python3 -m yt_dlp --add-header "Cookie:${COOKIES}" --get-title --no-playlist "${url}"`);
        const title = titleResult.stdout.trim().replace(/[^\w\s-]/g, '');
        console.log(`TITLE_START|${title}|TITLE_END`);

        let command = '';
        if (type === 'audio') {
            command = `python3 -m yt_dlp --add-header "Cookie:${COOKIES}" --no-playlist --no-check-certificate -x --audio-format mp3 -o "${outputPath}" --proxy "" "${url}"`;
        } else {
            command = `python3 -m yt_dlp --add-header "Cookie:${COOKIES}" --no-playlist --no-check-certificate -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" -o "${outputPath}" --proxy "" "${url}"`;
        }

        console.log(`Executing: ${command}`);
        const { stdout, stderr } = await execPromise(command);
        
        console.log('Success');
        process.exit(0);

    } catch (error) {
        console.error('Error:', error.message);
        process.exit(1);
    }
}

download();
