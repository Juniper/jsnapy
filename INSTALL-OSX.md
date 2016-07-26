Installation on OS X Mavericks
---------------
These instructions are community provided, tested with Python 2.7.5

### Operating Systems
- OS X Mavericks


When you upgrade your Mac to OS X Mavericks, Apple deletes your X11 and any addons under /Library/Python/2.7/site-packages.  There are plenty of posts on the Internet that describe how to restore your Python development environment, but this post will focus on the Juniper Junos JSNAPy framework.
 
Github has Mac client available that includes command line tools and a native GUI app. - https://help.github.com/articles/set-up-git.

Install Homebrew - http://brew.sh.

#### Installation:
 
If you have never used Python on your Mac, you will want to install X11 & Xcode.  Some Python packages have dependencies that rely on these packages.
1. Install X11 – The latest image can be found here.
2. Install Xcode - https://developer.apple.com/xcode/ - you may have to register as a developer, but there is no charge to get access to Xcode.
3. After Xcode is installed, install the command line tools.
  1. Open a Terminal window.
  2. Type: ```xcode-select –install```
4. Install Git or the GitHub client.
5. Create a symbolic link so that the tools we are about to install will compile without issues.
  1. Open a Terminal Window.
  2. Type: ```sudo ln -s /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.9.sdk/usr/include/libxml2/libxml/ /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.9.sdk/usr/include/libxml```
```
6. Need to add more steps.
