<h1>
    <img src="images/logo.png" height="32" alt="logo"/>
    Kliko's modding tool
</h1>

[<img alt="Website" src="https://img.shields.io/badge/website-353639?style=for-the-badge&logo=html5&logoColor=fff&labelColor=cc0037&color=353639">](https://thekliko.github.io/klikos-modding-tool)
[<img alt="GitHub License" src="https://img.shields.io/github/license/thekliko/klikos-mod-updater?style=for-the-badge&labelColor=cc0037&color=353639">](https://github.com/TheKliko/klikos-mod-updater/blob/main/LICENSE)
[<img alt="GitHub Release" src="https://img.shields.io/github/v/release/thekliko/klikos-mod-updater?filter=!v*.*.*-beta&style=for-the-badge&labelColor=cc0037&color=353639">](https://github.com/thekliko/klikos-mod-updater/releases/latest)
[<img alt="GitHub Downloads (all assets, latest release)" src="https://img.shields.io/github/downloads/thekliko/klikos-mod-updater/latest/total?style=for-the-badge&label=downloads&labelColor=cc0037&color=353639">](https://github.com/thekliko/klikos-mod-updater/releases)
[<img alt="Discord" src="https://img.shields.io/discord/1205938827437412422?style=for-the-badge&logo=discord&logoColor=fff&label=discord&labelColor=5865f2&color=353639">](https://discord.gg/nEjUwdSP9P)

<h3>Mod Updater</h3>
This tool can update your mods to the latest version of Roblox!
Made for mod developers, but it can be used by anyone.

<br>
<br>

<h3>Mod Generator</h3>
Generate mods, currently only supports the image atlas. Generate either a mod of 1 color or a gradient of 2 colors. Takes about 12 seconds depending on your hardware and internet speed

<br>
<br>
<h2 id="instructions">Instructions</h2>

> [!CAUTION]
> Warning: If you are running the source code directly, make sure that you are using Python 3.12.4! Any other version may not work.
<ul>
    <li>
        Download and extract the <a href="https://github.com/TheKliko/klikos-mod-updater/releases/latest">latest release</a>
    </li>
    <li>
        Make sure that the mod you want to update is properly formatted (<a href="https://i.imgur.com/swY0id5.png">example</a>)
    </li>
    <li>
        Go to the root folder of the mod that you want to update
    </li>
    <li>
        Create a new file named `info.json` and add either the file version or the version GUID that your mod was made for (file version is checked first, if it's not found then it checks for the GUID). The right format can be found in the example data below
    </li>
</ul>

Example data for info.json
```json
{
    "fileVersion": 676,
    "clientVersionUpload": "version-e1da58b32b1c4d64"
}
```

After completing these steps, go to where you extracted the updater tool and run mod_updater.py
<br>
<br>
<h2 id="requirements">Requirements</h2>
<ul>
    <li>A Windows PC (Optional)</li>
</ul>
<br>
<h2 id="help">Help & Support</h2>
If you are having any issues, feel free to ask them in my <a href="https://discord.gg/nEjUwdSP9P">support server</a>.
