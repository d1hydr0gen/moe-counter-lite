# Moe Counter Lite
Moe Counter Lite is recoded version of Moe-Counter with Improvments.<br>
It can handle averge 200 to 400 requests per seconds under 10-90ms(depends machine spec)<br>
I run Performance-Test for 30seconds and count reached 7500, averge responce time is 20ms.<br>
# How To Install
Download from github:
```git clone https://github.com/d1hydr0gen/moe-counter-lite.git```
Install Dependencies:
```npm install http url fs querystring sqlite3 xml2js base-64 mime```
Edit Configuration (if you want)
```nano moe.js```
Run ( recommended to use screen ):
```screen node moe.js```
# Only 1 theme?
Sadly Yes. but You can add theme easly.
open themes.json and add this
```
{
            "name": "your-theme-title",
            "letters":{
                "0":"assets/your-theme-dir/0.gif",
                "1":"assets/your-theme-dir/1.gif",
                "2":"assets/your-theme-dir/2.gif",
                "3":"assets/your-theme-dir/3.gif",
                "4":"assets/your-theme-dir/4.gif",
                "5":"assets/your-theme-dir/5.gif",
                "6":"assets/your-theme-dir/6.gif",
                "7":"assets/your-theme-dir/7.gif",
                "8":"assets/your-theme-dir/8.gif",
                "9":"assets/your-theme-dir/9.gif"
}
```
Done. Make it sure you added theme to assets folder.<br>
Please use 45x100(9:20) Images.<br>
You can test the access counter at: http://moecounterlite.rgba.uk/<br>
* I recommend to host it your self when you use it!
