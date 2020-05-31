# pihole-cname-update

This is a python adoption of the bash script I found
[here](https://discourse.pi-hole.net/t/cname-block-list/28369/23) written jpgpi250.

Since I don't know if we can cname block anything yet via web interface, and I kinda don't want to
execute SQL statements via bash I wrote this python script that expanded on that idea.

**NOTE: This script might be complete non-sense because you could maybe already do this from the
admin interface and I just didn't know that.**

Also there almost no error handling because I mainly wrote this for myself but stil
want to share it with others who might benifit from it.

If you have ideas on how to improve this scripts, PRs are welcome!

## What is the difference to the bash script

- This script can source multiple lists and not only one
- It will use prepared SQL statements
  - Though there is still the issue of downloading data from an unknown source.. but that depends on
    how you use this script
- Maybe it can be expanded for other things in the future

## Dependencies

- Python 3.6 or later
- [requests](https://requests.readthedocs.io/en/master/user/install/)
    - On Raspbian / Debian / Ubuntu: `sudo apt install python3-requests`
    - If you use something else follow the instructions above or:
        - Have another look if `requests` is packaged by your system package manager
        - And if that is not the case use `pip3 install requests` if you absolutely must

## Usage

Create a file named `pihole-cname-master.list`, or download it from here, and put it either next to the script or in `/etc`.
Each line on the list will be downloaded, parsed and added to the database. Every `#` comment will
be filtered before if the list isn't made for the PiHole.

After that you just have to execute cnameupdate.py for example like that:

```bash
python3 cnameupdate.py
```
