# -*- coding: utf-8 -*-
import datetime
import glob
import logging
import os
import shutil
import sys
from multiprocessing import Pool, cpu_count, freeze_support
from multiprocessing_logging import install_mp_handler

from robot import rebot
from robot.conf import RobotSettings
from robot.model import SuiteVisitor
from robot.output import LOGGER
from robot.run import RobotFramework, run, USAGE
from robot.running import TestSuiteBuilder
from robot.utils import unic, Application

# Syntax sugar.
_ver = sys.version_info
is_py2 = (_ver[0] == 2)  #: Python 2.x?
is_py3 = (_ver[0] == 3)  #: Python 3.x?
if is_py2:
    from itertools import izip as zip, repeat
if is_py3:
    from itertools import repeat


class TeardownCleaner(SuiteVisitor):
    def end_test(self, test):
        if not test.keywords.teardown:
            test.keywords.create(name='Run Keywords', type='teardown',
                                 args=['Run Keyword And Ignore Error', 'Close Browser', 'AND',
                                       'Run Keyword And Ignore Error', 'Disconnect From Database'])


logger = logging.getLogger('parabot')
console = logging.StreamHandler()
logger.addHandler(console)
logger.setLevel(logging.DEBUG)
# logging.getLogger(name='requests').setLevel(logging.WARNING)
# logging.getLogger(name='selenium').setLevel(logging.WARNING)

USAGE_EXT = """ExtOptions  
==========  
 -p --processes num       How many processes to be run.=========="""


class Parabot(RobotFramework):
    def __init__(self):
        first_half, last_half = USAGE.split("Options\n=======", 1)
        extended_usage = "\n".join([first_half, USAGE_EXT, last_half])
        Application.__init__(self, extended_usage, arg_limits=(1,),
                             env_options='ROBOT_OPTIONS', logger=LOGGER)
        self.output_dir = None
        self.data_source = None
        self.long_names = []

    def main(self, data_sources, **options):
        settings = RobotSettings(options)
        LOGGER.register_console_logger(**settings.console_output_config)
        LOGGER.info("Settings:\n%s" % unic(settings))
        suite = TestSuiteBuilder(settings['SuiteNames'],
                                 settings['WarnOnSkipped'],
                                 settings['Extension']).build(*data_sources)
        suite.configure(**settings.suite_config)
        self._support_python_path(options)
        self._split_tests(suite)  # 递归，找到所有的tests, 写入self.long_names
        self._assert_data_source(data_sources)  # 只取第一个DataSource, 写入self.data_source
        self._assert_test_count()  # 如果没有要测试的, 直接退出, 返回码: 1
        self.output_dir = settings['OutputDir']
        self.clean_output_dir()  # 删掉主要输出目录下所有东东, 类似rm -rf self.output_dir
        self.log_debug_info(options)
        p_num = (int(options['processes']) if 'processes' in options else 2 * cpu_count())
        start_time, end_time = self.parallel_run(options, p_num)
        self.merge_report(start_time, end_time)

    def _support_python_path(self, opts):
        if self._ap._auto_pythonpath and opts.get('pythonpath'):
            sys.path = self._ap._get_pythonpath(opts['pythonpath']) + sys.path

    def _split_tests(self, suite):
        if suite.suites:
            for sub_suite in suite.suites:
                self._split_tests(sub_suite)
        else:
            for test in suite.tests:
                self.long_names.append(test.longname)  # 从根的suite到叶的testcase串起来的longname

    def _assert_data_source(self, data_sources):
        if len(data_sources) > 1:
            raise ValueError("Support only ONE data source")
        self.data_source = data_sources[0]

    def _assert_test_count(self):
        if len(self.long_names) <= 0:
            exit(1)

    def clean_output_dir(self):
        path = self.output_dir
        if os.path.isdir(path) and not os.path.islink(path):
            shutil.rmtree(path)
        elif os.path.exists(path):
            os.remove(path)
        # os.mkdir(path)

    def log_debug_info(self, options):
        logger.debug("robot_options:\n" + "\n".join(["{}->{}".format(x[0], x[1]) for x in options.items()]))
        logger.debug("tests({}) to run:\n".format(len(self.long_names)) + "\n".join(self.long_names))
        logger.debug("data_source: " + self.data_source)

    def parallel_run(self, options, p_num):
        start_time = datetime.datetime.now()
        logger.info('run start at: {}'.format(start_time))

        freeze_support()  # 兼容windows, 避免由于程序frozen导致的RuntimeError
        install_mp_handler()
        pool = Pool(processes=p_num)
        pool.map_async(run_robot_star, zip(repeat(options), self.long_names, repeat(self.data_source)))
        pool.close()
        pool.join()

        end_time = datetime.datetime.now()
        logger.info('run end at: {}'.format(end_time))
        logger.info('run elapsed time: {}'.format(end_time - start_time))
        return start_time, end_time

    def merge_report(self, start_time, end_time):
        path = os.path.join(self.output_dir, '*', 'output.xml')
        outputs = glob.glob(path)
        options = {
            "merge": True,
            "loglevel": "WARN",
            "starttime": str(start_time),
            "endtime": str(end_time),
            "outputdir": self.output_dir,
            "output": "output.xml"
        }
        with open(os.path.join(self.output_dir, 'merge.log'), 'w') as stdout:
            rebot(*outputs, stdout=stdout, **options)


def run_robot_star(options_test_source):  # compatible for python2
    """Convert `f((options,test,source))` to `f(options,test, data_source)` call."""
    return run_robot(*options_test_source)


def run_robot(options, test, data_source):
    sub_dir = os.path.join(options['outputdir'], test)
    os.makedirs(sub_dir)
    options['outputdir'] = sub_dir
    options['report'] = None
    options['test'] = test
    options['prerunmodifier'] = TeardownCleaner()
    process_reportportal_options(options)
    stdout = os.path.join(sub_dir, 'stdout.log')
    stderr = os.path.join(sub_dir, 'stderr.log')
    with open(stdout, 'w') as stdout, open(stderr, 'w') as stderr:
        ret_code = run(data_source, stdout=stdout, stderr=stderr, **options)
    logger.info('{pid}:\t[{status}] {long_name}'
                .format(pid=os.getpid(), status='PASS' if ret_code == 0 else "FAIL", long_name=test))
    return ret_code


def process_reportportal_options(options):
    if 'variable' not in options:
        return
    for i, var in enumerate(options['variable']):
        if str(var).startswith('RP_LAUNCH'):
            options['variable'][i] = "RP_LAUNCH:" + options['test']
            # TODO: download agent binary code


def run_cli(arguments, exit=True):
    """Command line execution entry point for running tests.  
    See robot.run.run_cli"""
    return Parabot().execute_cli(arguments, exit=exit)


if __name__ == '__main__':
    run_cli(sys.argv[1:])
