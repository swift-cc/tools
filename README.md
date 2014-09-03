# Tools
<b>
## Swift-X
<b>
### Introduction

swift-x is a python script that simplifies the compiling of Swift and Objective-C(++) code into object files.

Once installed, you can easily compile any number of Swift and Objective-C(++) files into object files that are targeted for armv7.


###Overview

swift-x is a two stage wrapper for clang and the swift compiler that uses the Android NDK tools to produce android compatible .o files.

The first stage uses clang or swift to compile source code and emit LLVM-IR code which is passed to the Android second stage tools which compile the IR into .o files.

All of this is completely handled by the tool, and so the tool is super easy to use.

    script-x file.mm file2.swift

This will produce file.o and file2.o which can be linked using the Android NDK library archiver or linker.

For other info, use the following to get command line help.

    script-x -h
 

### Installation

In order to be able to use the tool from anywhere, i.e. in Android.mk or other makefiles, it needs to be added to the environment path variable.

Open up your .bash_profile or whatever file you use for setting up your environment, and add the following line before the path export.

    PATH=$PATH:<your path to swift-x.py>
    
Remember to re-parse the profile using source .bash_profile or whatever your profile name is.

Once installed, this script will be available from anywhere and can be used as a drop in compiler for compiling Swift and Objective-C(++) into object files for Android.

### Configuration

There is an example configuration file **config_example.txt**

There are four variables you need to setup in order for the tool to work. The config file must be in the same directory as the tool, and must be named **config.txt**. It is a simple key value pair file that has variables that tell the tool where Xcode, Android SDK/NDK are etc.

The variable are at the top of the file, and are named as follows.

    MODULE_NAME = <your module name>
    
    XCODE = <path to xcode.app>  
    
    ANDROID_SDK = <path to android sdk>
    
    ANDROID_NDK = <path to android ndk>
    
Once these variables have been set, the tool should work out of the box. The rest of the variables in the config file are derived from these four config variables.