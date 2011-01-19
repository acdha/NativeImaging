# encoding: utf-8

import platform
import urllib
import logging


def save_to_codespeed(url, project, commitid, executable, benchmark, result_value, **kwargs):
    """
    
    Mandatory:
    
    :param url:
        Codespeed server endpoint (e.g. `http://codespeed.example.org/result/add/`)
    :param project:
        Project name
    :param commitid:
        VCS identifier
    :param executable:
    :param benchmark:
    :param float result_value:

    Optional:
    
    :environment:
        System description
    :param date revision_date:
        Optional, default will be either VCS commit, if available, or the
        current date
    :param date result_date:
        Optional
    :param float std_dev:
        Optional
    :param float max:
        Optional
    :param float min:
        Optional
    """

    data = {
        'project': project,
        'commitid': commitid,
        'executable': executable,
        'benchmark': benchmark,
        'result_value': result_value,
    }
    data.update(kwargs)
    
    if not data.get('environment', None):
        data['environment'] = platform.platform(aliased=True)

    f = urllib.urlopen(url, urllib.urlencode(data))

    response = f.read()
    status = f.getcode()
    
    if status == 200:
        log_f = logging.debug
    else:
        log_f = logging.warning

    log_f("Server %s: HTTP %s: %s", url, status, response)

    f.close()


if __name__ == "__main__":
    pass
