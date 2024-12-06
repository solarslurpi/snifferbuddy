
## Enabling/Disabling Features
An example of this is enabling suport for the `SCD40` sensor.  By default, the Tasmota firmware does not include the `SCD40` driver in the build. To enable it, the easiest way is to follow the instructions:
- [The YouTube video _Compiling your own custom Tasmota on the web - No installs, no coding!_](https://www.youtube.com/watch?v=vod3Woj_vrs)
- [The Tasmota documentation covering compiling with Gitpod](https://tasmota.github.io/docs/Compile-your-build/)

Once the editor is loaded, open up the file `tasmota/my_user_config.h`. Uncomment out the `define` line for the `SCD40` sensor. 

_Note:_ There are sensors that are loaded taking up memory that are not used. I comment out some of these to save memory. However, I do this somewhat randomly.  In the future, I will add a tool to help with this.

Then follow the steps in 