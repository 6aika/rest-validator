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
* `python -m rv --html report.html examples.issue_reporting`
  (add `--endpoint` if required)
* You should find a `report.html` page in your working directory, detailing
  the tests that were run.

Basic Principles & Development
------------------------------

Now that you have seen the result, maybe we should look at how to get there!

The principal objects at the moment are

* **Validators** such as `examples.issue_reporting.IssueReportingValidator`,
  which have user-settable options and are command line accessible, and
  consist of
* **Suites** such as `rv.suites.lists.ListTester` which generate and
  group up logically similar
* **Tests** such as `rv.tests.params.SingleParamTest` which are the
  lowest, simplest unit of execution and encapsulate a single attempt at
  verify something.  (Unlike regular unit tests though, these tests may yield
  several errors).

In addition, there are supporting classes such as `rv.params.Param`, which
is what the `ListTester` suite uses to figure out which parameters should be
tested by the `SingleParamTest` and `MultiParamTest` classes.

* To implement validation against a new REST API, just base it on (and I mean copy-paste)
`examples.issue_reporting.IssueReporting`.
* To implement new tests, subclass `rv.suites.base.Suite` and `rv.tests.base.Test`.
  * Pull requests welcome!
