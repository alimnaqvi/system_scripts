# My Linux scripts

## Disk usage

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
