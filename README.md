# My Linux scripts

Instead of installing extensions for everything, I prefer to write my own lightweight scripts to automate simple tasks like. This gives me full control over what happens, I don't "pay for anything I don't use" (i.e., avoid bloatware), and it provides me with a great learning opportunity.

For scheduling the running of the scripts, while `crontab` is a straightforward way, it has many limitations. I prefer to use `systemd`, which is a powerful, modern method of scheduling tasks. Since it is a bit tricky to set up, I have written the script `set_all_schedules.sh` to automate some of it (the script automatically sets systemd tasks for the automation scripts in this repo that need scheduling).

## Auto dark theme

A script that changes the GNOME color scheme depending on the time of day (dark between 8pm and 6am).

`systemd` is used to run the script at the specified times, and at startup.

## Wallpaper changer

A slideshow of wallpapers that changes every 15 minutes and differentiates between wallpapers for dark vs. light theme.

## Disk usage

A script to check, log, and show history of the size of the entire distro installation. Run the script without any arguments to see usage information.

Add an alias to `.bashrc`/`.zshrc` to run the script easily.

```bash
alias distro_size='<path-to-this-repo>/system_scripts/disc_usage/distro_size.sh'
```

If you want to use `crontab` instead of `systemd`, you can do the following to automate logging maximum once every day:

```bash
sudo crontab -e
```

Add the following line to the crontab (remember to replace `<path-to-this-repo>`):

```
@reboot <path-to-this-repo>/disc_usage/distro_size.sh --cron
```

## Fix CAps LOck delay

Linux desktop environments, such as GNOME, often have this "feature" enabled by default that adds a delay to prevent accidental Caps Lock activation. For fast typists, it's a disaster because YOu WIll BE TYping LIke THis.

`fix-capslock-delay.sh` script takes the *current* keyboard map, surgically replaces the faulty Caps Lock definition with a good one, and then immediately loads that fixed map back into the system.

But a reboot will completely undo its changes, which is why it needs to be run at startup. A service like `cron` or, the better method, `systemd` can be used to always run this script on startup. Alternatively, Linux desktop GUIs often provide a front-end to easily specify tasks/scripts/applications that should be run at startup.
