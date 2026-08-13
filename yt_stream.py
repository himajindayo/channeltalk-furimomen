"""
yt_stream.py
YouTubeの動画・音声ストリームリンクを取得するユーティリティ

使い方:
    python yt_stream.py <YouTube URL> [オプション]

オプション:
    --quality best|worst|<height>  映像品質 (デフォルト: best)
    --audio-only                   音声ストリームのみ取得
    --hls                          HLS (m3u8) ストリームURLを取得（ライブ配信向け）
    --list                         利用可能な全フォーマットを一覧表示
    --json                         結果をJSON形式で出力

Cookie指定方法（認証が必要な動画向け）:
    --cookies <Netscape形式のcookieファイルパス>
    --cookies-from-browser <ブラウザ名>  例: chrome / firefox / edge

Cookie文字列を直接渡す場合はライブラリとして使用し、
cookie_str 引数に "name=value; name2=value2" 形式で渡す。
"""

import yt_dlp
import json
import argparse
import sys
import tempfile
import os
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class StreamInfo:
    """取得したストリーム情報"""
    title: str
    url: str
    audio_url: Optional[str]
    format_id: str
    ext: str
    protocol: Optional[str]
    resolution: Optional[str]
    fps: Optional[float]
    vcodec: Optional[str]
    acodec: Optional[str]
    filesize: Optional[int]
    is_merged: bool

    def to_dict(self) -> dict:
        """JSON シリアライズ可能な dict に変換"""
        return asdict(self)

    def to_json(self, **kwargs) -> str:
        """JSON 文字列に変換。kwargs は json.dumps に渡される"""
        kwargs.setdefault("ensure_ascii", False)
        kwargs.setdefault("indent", 2)
        return json.dumps(self.to_dict(), **kwargs)


def _build_stream_info(info: dict, audio_url: Optional[str] = None, is_merged: bool = True) -> StreamInfo:
    return StreamInfo(
        title=info.get("title", "Unknown"),
        url=info["url"],
        audio_url=audio_url,
        format_id=info.get("format_id", ""),
        ext=info.get("ext", ""),
        protocol=info.get("protocol"),
        resolution=info.get("resolution"),
        fps=info.get("fps"),
        vcodec=info.get("vcodec"),
        acodec=info.get("acodec"),
        filesize=info.get("filesize") or info.get("filesize_approx"),
        is_merged=is_merged,
    )


def _cookie_opts(
    cookie_str: Optional[str] = None,
    cookie_file: Optional[str] = None,
    browser: Optional[str] = None,
) -> dict:
    """
    Cookie関連のyt-dlpオプションを返す。

    Parameters
    ----------
    cookie_str  : "name=value; name2=value2" 形式の文字列（ブラウザのDevToolsからコピー可）
    cookie_file : Netscape形式のcookieファイルパス（cookies.txt）
    browser     : ブラウザ名 "chrome" / "firefox" / "edge" / "safari" など
                  yt-dlpが直接ブラウザのCookieストアから読み込む
    """
    opts = {}
    if browser:
        opts["cookiesfrombrowser"] = (browser, None, None, None)
    elif cookie_file:
        opts["cookiefile"] = cookie_file
    elif cookie_str:
        # 文字列 → 一時的なNetscape形式ファイルに変換して渡す
        # （呼び出し元でファイルを削除すること）
        opts["_cookie_str"] = cookie_str  # 後で処理するマーカー
    return opts


def _write_cookie_file(cookie_str: str) -> str:
    """
    "name=value; name2=value2" 形式のCookie文字列を
    Netscape形式の一時ファイルに書き出してパスを返す。
    使い終わったら呼び出し元で os.unlink() すること。
    """
    lines = ["# Netscape HTTP Cookie File\n"]
    for pair in cookie_str.split(";"):
        pair = pair.strip()
        if "=" not in pair:
            continue
        name, _, value = pair.partition("=")
        # domain / path / secure / expires は汎用値で埋める
        lines.append(f".youtube.com\tTRUE\t/\tFALSE\t2147483647\t{name.strip()}\t{value.strip()}\n")

    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8")
    tmp.writelines(lines)
    tmp.flush()
    tmp.close()
    return tmp.name


def _make_ydl_opts(
    fmt: str,
    cookie_str: Optional[str] = None,
    cookie_file: Optional[str] = None,
    browser: Optional[str] = None,
) -> tuple[dict, Optional[str]]:
    """
    yt-dlp オプション dict と、後で削除すべき一時ファイルパス（なければ None）を返す。
    """
    opts = {
        "format": fmt,
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "noplaylist": True,
    }
    tmp_path = None

    if browser:
        opts["cookiesfrombrowser"] = (browser, None, None, None)
    elif cookie_file:
        opts["cookiefile"] = cookie_file
    elif cookie_str:
        tmp_path = _write_cookie_file(cookie_str)
        opts["cookiefile"] = tmp_path

    return opts, tmp_path


def get_stream_links(
    url: str,
    quality: str = "best",
    audio_only: bool = False,
    cookie_str: Optional[str] = None,
    cookie_file: Optional[str] = None,
    browser: Optional[str] = None,
) -> StreamInfo:
    """
    YouTube動画の統合ストリーム（映像+音声が1URL）を返す。

    Parameters
    ----------
    url         : YouTube動画のURL
    quality     : 'best' / 'worst' / 高さpx文字列 (例: '720')
    audio_only  : True にすると音声ストリームのみ取得
    cookie_str  : ブラウザのDevToolsからコピーしたCookie文字列
                  例: "SAPISID=xxx; __Secure-3PAPISID=yyy; ..."
    cookie_file : Netscape形式のcookieファイルパス
    browser     : ブラウザ名 ("chrome" / "firefox" / "edge" / "safari")
    """
    if audio_only:
        fmt = "bestaudio/best"
    elif quality == "best":
        fmt = "best[vcodec!=none][acodec!=none]"
    elif quality == "worst":
        fmt = "worst[vcodec!=none][acodec!=none]"
    else:
        fmt = f"best[vcodec!=none][acodec!=none][height<={quality}]"

    opts, tmp_path = _make_ydl_opts(fmt, cookie_str, cookie_file, browser)
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
    finally:
        if tmp_path:
            os.unlink(tmp_path)

    if not info.get("url"):
        raise ValueError(
            "統合ストリームが見つかりませんでした。\n"
            "--list で利用可能なフォーマットを確認してください。"
        )
    return _build_stream_info(info)


def get_hls_url(
    url: str,
    quality: str = "best",
    cookie_str: Optional[str] = None,
    cookie_file: Optional[str] = None,
    browser: Optional[str] = None,
) -> StreamInfo:
    """
    HLS (m3u8) ストリームのURLを取得する。主にライブ配信向け。

    注意:
      - 通常動画にはHLSが存在しないため ValueError を送出する。
      - 有効期限が短いため取得後すぐに使用すること。
      - ffmpeg で保存: ffmpeg -i "<m3u8_url>" -c copy output.mp4
    """
    check_opts, tmp_path = _make_ydl_opts("best", cookie_str, cookie_file, browser)
    try:
        with yt_dlp.YoutubeDL(check_opts) as ydl:
            info_all = ydl.extract_info(url, download=False)
    finally:
        if tmp_path:
            os.unlink(tmp_path)

    hls_formats = [
        f for f in info_all.get("formats", [])
        if f.get("protocol") in ("m3u8_native", "m3u8")
    ]
    if not hls_formats:
        available = sorted({f.get("protocol", "unknown") for f in info_all.get("formats", [])})
        raise ValueError(
            f"この動画にはHLS (m3u8) フォーマットが存在しません。\n"
            f"利用可能なプロトコル: {available}\n"
            f"ヒント: HLSはライブ配信・プレミア公開中の動画に存在することが多いです。"
        )

    if quality == "best":
        fmt = (
            "best[protocol=m3u8_native][vcodec!=none][acodec!=none]"
            "/best[protocol=m3u8][vcodec!=none][acodec!=none]"
            "/best[protocol=m3u8_native]/best[protocol=m3u8]"
        )
    elif quality == "worst":
        fmt = (
            "worst[protocol=m3u8_native][vcodec!=none][acodec!=none]"
            "/worst[protocol=m3u8][vcodec!=none][acodec!=none]"
            "/worst[protocol=m3u8_native]/worst[protocol=m3u8]"
        )
    else:
        fmt = (
            f"best[protocol=m3u8_native][height<={quality}][vcodec!=none][acodec!=none]"
            f"/best[protocol=m3u8][height<={quality}][vcodec!=none][acodec!=none]"
            f"/best[protocol=m3u8_native][height<={quality}]"
            f"/best[protocol=m3u8][height<={quality}]"
        )

    opts, tmp_path = _make_ydl_opts(fmt, cookie_str, cookie_file, browser)
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
    finally:
        if tmp_path:
            os.unlink(tmp_path)

    if not info.get("url"):
        raise ValueError("HLS URLの取得に失敗しました。")
    return _build_stream_info(info)


def list_formats(
    url: str,
    cookie_str: Optional[str] = None,
    cookie_file: Optional[str] = None,
    browser: Optional[str] = None,
) -> list[dict]:
    """利用可能な全フォーマットをリストで返す"""
    opts, tmp_path = _make_ydl_opts("best", cookie_str, cookie_file, browser)
    opts.pop("format", None)  # list時はformat指定不要
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
    finally:
        if tmp_path:
            os.unlink(tmp_path)

    return [
        {
            "format_id": f.get("format_id"),
            "ext":       f.get("ext"),
            "protocol":  f.get("protocol"),
            "resolution": f.get("resolution", "audio only"),
            "fps":       f.get("fps"),
            "vcodec":    f.get("vcodec"),
            "acodec":    f.get("acodec"),
            "filesize":  f.get("filesize") or f.get("filesize_approx"),
            "url":       f.get("url"),
        }
        for f in info.get("formats", [])
    ]


# ─── CLI ───────────────────────────────────────────────────────────────────────

def _fmt_size(n: Optional[int]) -> str:
    if not n:
        return "不明"
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def main():
    parser = argparse.ArgumentParser(
        description="YouTube ストリームリンク取得ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Cookie指定例:
  --cookies-from-browser chrome          Chromeから自動取得
  --cookies cookies.txt                  Netscape形式ファイル指定
  --cookie-str "SAPISID=xxx; ..."        文字列で直接指定
        """
    )
    parser.add_argument("url", help="YouTube動画のURL")
    parser.add_argument("--quality", default="best",
                        help="映像品質: best / worst / 高さpx (例: 720)")
    parser.add_argument("--audio-only", action="store_true",
                        help="音声ストリームのみ取得")
    parser.add_argument("--hls", action="store_true",
                        help="HLS (m3u8) ストリームURLを取得（主にライブ配信向け）")
    parser.add_argument("--list", action="store_true",
                        help="利用可能な全フォーマットを一覧表示")
    parser.add_argument("--json", action="store_true",
                        help="JSON形式で出力")
    # Cookie オプション
    parser.add_argument("--cookies", metavar="FILE",
                        help="Netscape形式のcookieファイルパス")
    parser.add_argument("--cookies-from-browser", metavar="BROWSER",
                        help="ブラウザ名 (chrome / firefox / edge / safari)")
    parser.add_argument("--cookie-str", metavar="STRING",
                        help="Cookie文字列 (\"name=val; name2=val2\" 形式)")
    args = parser.parse_args()

    cookie_kwargs = dict(
        cookie_str=args.cookie_str,
        cookie_file=args.cookies,
        browser=args.cookies_from_browser,
    )

    try:
        if args.list:
            formats = list_formats(args.url, **cookie_kwargs)
            if args.json:
                print(json.dumps(formats, ensure_ascii=False, indent=2))
            else:
                print(f"{'ID':<12} {'拡張子':<6} {'プロトコル':<20} {'解像度':<14} {'FPS':<6} {'映像codec':<14} {'音声codec':<12} {'サイズ'}")
                print("-" * 105)
                for f in formats:
                    print(
                        f"{f['format_id']:<12} {f['ext']:<6} "
                        f"{str(f['protocol'] or ''):<20} "
                        f"{str(f['resolution']):<14} {str(f['fps'] or ''):<6} "
                        f"{str(f['vcodec'] or ''):<14} {str(f['acodec'] or ''):<12} "
                        f"{_fmt_size(f['filesize'])}"
                    )
            return

        if args.hls:
            info = get_hls_url(args.url, quality=args.quality, **cookie_kwargs)
        else:
            info = get_stream_links(args.url, quality=args.quality,
                                    audio_only=args.audio_only, **cookie_kwargs)

        if args.json:
            print(json.dumps(asdict(info), ensure_ascii=False, indent=2))
        else:
            print(f"\n タイトル  : {info.title}")
            print(f"   フォーマット: {info.format_id} ({info.ext})")
            print(f"   プロトコル  : {info.protocol or 'N/A'}")
            print(f"   解像度    : {info.resolution or 'N/A'}  FPS: {info.fps or 'N/A'}")
            print(f"   映像codec : {info.vcodec or 'N/A'}")
            print(f"   音声codec : {info.acodec or 'N/A'}")
            print(f"   サイズ    : {_fmt_size(info.filesize)}")
            print(f"\n📺 URL:\n  {info.url}")
            if info.audio_url:
                print(f"\n🎵 音声URL（分離）:\n  {info.audio_url}")
            print()

    except (yt_dlp.utils.DownloadError, ValueError) as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()