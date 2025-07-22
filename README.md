# My Linux scripts

## Disk usage

A script to check, log, and show history of the size of the entire distro installation. Run the script without any arguments to see usage information.

Add an alias to `.bashrc`/`.zshrc` to run the script easily.

```bash
alias distro_size='<path-to-this-repo>/system_scripts/disc_usage/distro_size.sh'
```

Automate logging maximum once every day:

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
