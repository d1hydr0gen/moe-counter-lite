const http = require('http');
const url = require('url');
const fs = require('fs');
const querystring = require('querystring');
const sqlite3 = require('sqlite3');
const xml2js = require('xml2js');
const base64 = require('base-64');
const mime = require('mime');

// DO NOT CHANGE THIS
const counters = [];
const themes = [];
////////////////////////

// Port and Binding Settings
const BIND = "0.0.0.0";
const PORT = 8000;

// Default Theme
const default_theme = "gelbooru";

// Advanced Settings
// If count reaches MAX, it will stop counting
const MAX = 9999999;
// Database Name (only SQLITE3 supported for now)
const database = "database.db";
// Update Duration (seconds)
const duration = 5;

class Counter {
    constructor(id, count) {
        this.id = id;
        this.count = count;
        this.svg = [];
    }
}

class Theme {
    constructor(name) {
        this.name = name;
        this.letters = [];
    }
}

class Letter {
    constructor(letter, url) {
        this.letter = letter;
        this.url = url;
    }
}

function init() {
    const db = new sqlite3.Database(database);
    db.run(`
        CREATE TABLE IF NOT EXISTS count (
            id TEXT PRIMARY KEY,
            count INTEGER DEFAULT 0
        )`);
    db.all('SELECT * FROM count', (err, rows) => {
        if (err) {
            console.error(err.message);
            return;
        }
        rows.forEach(row => {
            counters.push(new Counter(row.id, row.count));
        });
        db.close();
        initTheme();
    });
}

function encodeFileToBase64(file_path) {
    try {
        console.log(`Encoding file: ${file_path}`);
        const file_content = fs.readFileSync(file_path, { encoding: 'base64' });
        const mime_type = mime.getType(file_path);
        return `data:${mime_type};base64,${file_content}`;
    } catch (error) {
        console.error(`Error encoding file: ${file_path}`, error);
        return null;
    }
}



function initTheme() {
    const themeData = require('./themes.json');
    themeData.themes.forEach(theme => {
        const themeObj = new Theme(theme.name);
        for (const [key, value] of Object.entries(theme.letters)) {
            themeObj.letters.push(new Letter(key, encodeFileToBase64(value)));
        }
        themes.push(themeObj);
    });
}

function createSvg(ct, theme) {
    const width = String(MAX).length * 45;

    const svgParts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="${width}" height="100" version="1.1" style="image-rendering: pixelated;">`,
        '<title>Moe Count</title>',
        '<g>',
    ];

    const st = String(ct).padStart(String(MAX).length, '0');
    const imageUrls = st.split('').map(digit => theme.letters[Number(digit)].url);

    imageUrls.forEach((url, index) => {
        svgParts.push(`<image x="${index * 45}" y="0" width="45" height="100" xlink:href="${url}"/>`);
    });

    svgParts.push('</g>', '</svg>');

    return svgParts.join('\n');
}

function update() {
    setInterval(() => {
        counters.forEach(counter => {
            const svgs = themes.map(theme => createSvg(counter.count, theme));
            counter.svg = svgs;
            const id = counter.id;
            const count = counter.count;
            const db = new sqlite3.Database(database);

            // Use the INSERT OR REPLACE INTO statement to update or insert a record.
            db.run('INSERT OR REPLACE INTO count (id, count) VALUES (?, ?)', [id, count], err => {
                if (err) {
                    console.error(err.message);
                }
                db.close();
            });
        });
    }, duration * 1000);
}


function getThemeIdByName(name) {
    const themeIndex = themes.findIndex(theme => theme.name === name);
    if (themeIndex !== -1) {
        return themeIndex; // テーマが見つかった場合、インデックスを返す
    } else {
        return getThemeIdByName(default_theme); // デフォルトテーマを検索する
    }
}

function count(id,themename) {
    const counter = counters.find(counter => counter.id === id);
    if (counter) {
        if (counter.count !== MAX) {
            counter.count += 1;
            console.log(id + " " + counter.count);
        }
        return counter.svg[getThemeIdByName(themename)];
    }
    const newCounter = new Counter(id, 1);
    counters.push(newCounter);
    const svgs = themes.map(theme => createSvg(1, theme));
    newCounter.svg = svgs;
    console.log(id + " " + newCounter.count);
    return newCounter.svg[getThemeIdByName(themename)];
}

const server = http.createServer((req, res) => {
    const parsedUrl = url.parse(req.url);
    const queryParameters = querystring.parse(parsedUrl.query);
    
    if (parsedUrl.pathname === '/') {
        fs.readFile('views/index.html', (err, data) => {
            if (err) {
                res.writeHead(500);
                res.end('Internal Server Error');
                return;
            }
            res.writeHead(200, { 'Content-Type': 'text/html' });
            res.end(data);
        });
    } else if (/^\/get\/\w+/.test(parsedUrl.pathname)) {
        const name = parsedUrl.pathname.split('/').pop().split('?')[0];
        res.writeHead(200, { 'Content-Type': 'image/svg+xml' });
        var themename = default_theme;
        if("theme" in queryParameters){
            themename = queryParameters["theme"];
        }
        res.end(count(name,themename));
    } else {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('Not Found');
    }
});

server.listen(PORT, BIND, () => {
    console.log("Initializing...");
    init();
    console.log("Doe! Starting Webserver...");
    console.log(`Serving at http://${BIND}:${PORT}`);
    update();
});
