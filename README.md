API Validator
=============

This project is an attempt to build a framework for validating RESTful APIs
beyond just schema enforcement (though that is done too).

Try it out
----------

As an initial example, one can validate the list endpoint and filtering
for the https://github.com/6aika/issue-reporting API.

* Set up the above repository and import some issues; leave the server
  running on `127.0.0.1:8000` (or elsewhere, see below)
* Set `PYTHONPATH` to `.` (so `rv` may be imported)
* `python examples/validate_issue_reporting_list.py` (add `--endpoint` if
  required)

