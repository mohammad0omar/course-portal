# Course Portal (Level 4)

This is the Course Portal from the lecture. It is vulnerable on purpose: the
access control and CSRF flaws in it are the lab. It listens on `127.0.0.1`
only. Never expose it to a network, and never put real data in it.

## Get it

```
git clone https://github.com/mohammad0omar/course-portal.git
cd course-portal
```

## Setup

You need Python 3.10 or newer.

macOS or Linux:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Windows (PowerShell):

```
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

If PowerShell refuses to run the activate script, run
`Set-ExecutionPolicy -Scope Process RemoteSigned` first, then try again.

Open http://127.0.0.1:5002 in your browser.

## Accounts

All passwords are `Portal1234!`.

| Username | Role |
|---|---|
| lina | student (CMPS 215) |
| sami | student (CMPS 202) |
| omar | TA (CMPS 215) |
| rana | TA (CMPS 202), also enrolled in CMPS 202 |
| dr_haddad | instructor (CMPS 215) |
| dr_khoury | instructor (CMPS 202) |
| registrar | registrar |
| chair | department chair |

## Reset

To rebuild the seed data from scratch:

```
python run.py --reset
```

## Tests

```
python -m pytest -q
```

25 tests fail when you start, and 16 pass. That is correct. The failing tests
describe the policy, the access control attacks and the CSRF attacks your fix
must stop. When your fix is right, they all pass.
