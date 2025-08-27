import { Config } from "./src/config";

export const defaultConfig: Config = {
  url: "https://novel.tingroom.com/html/36/174.html",
  match: "https://novel.tingroom.com/html/36/**",
  selector: "body", // 抓取整个body内容，包含英文和中文
  maxPagesToCrawl: 50,
  outputFileName: "novel_output.json",
  maxTokens: 2000000,
  // 排除不需要的资源文件
  resourceExclusions: [
    "png",
    "jpg",
    "jpeg",
    "gif",
    "svg",
    "css",
    "js",
    "ico",
    "woff",
    "woff2",
    "ttf",
    "eot",
    "otf",
    "mp4",
    "mp3",
    "webm",
    "ogg",
    "wav",
    "flac",
    "aac",
    "zip",
    "tar",
    "gz",
    "rar",
    "7z",
  ],
};
