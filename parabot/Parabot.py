# -*- coding: utf-8 -*-
from itertools import repeat
from multiprocessing import cpu_count, freeze_support

from robot.conf import RobotSettings
from robot.output import LOGGER
from robot.run import RobotFramework, USAGE, run
from robot.running import TestSuiteBuilder

from robot.utils import Application, unic
import sys
import os

try:
    from itertools import izip as zip
except ImportError:  # python3
    pass

USAGE_EXT = """parabot_options:
===============
 -p --processes num       How many processes to be run.
"""


class Parabot(RobotFramework):
    def __init__(self):
        first_half, last_half = USAGE.split("Options\n=======", 1)
        extended_usage = "\n".join([first_half, USAGE_EXT, last_half])
        Application.__init__(self, extended_usage, arg_limits=(1,),
                             env_options='ROBOT_OPTIONS', logger=LOGGER)
        self.long_names = []

    def main(self, data_sources, **options):
        settings = RobotSettings(options)
        LOGGER.register_console_logger(**settings.console_output_config)
        LOGGER.info('Settings:\n%s' % unic(settings))
        suite = TestSuiteBuilder(settings['SuiteNames'],
                                 settings['WarnOnSkipped'],
                                 settings['Extension']).build(*data_sources)
        suite.configure(**settings.suite_config)
        p_num = int(options['processes']) if "processes" in options else 2 * cpu_count()
        data_sources = data_sources[0]  # support only one data_source
        self._split_tests(suite)
        self.parallel_run(options, data_sources)

    def _split_tests(self, suite):
        if suite.suites:
            for suite in suite.suites:
                self._split_tests(suite)
        else:
            for test in suite.tests:
                self.long_names.append(test.longname)

    def parallel_run(self, options, data_source, process_num=1):
        import multiprocessing
        freeze_support()
        pool = multiprocessing.Pool(process_num)
        result = pool.map_async(robot_star, zip(repeat(options), self.long_names, repeat(data_source)))
        result.wait()
        if result.ready():  # 线程函数是否已经启动了
            if result.successful():  # 线程函数是否执行成功
                print(result.get())  # 线程函数返回值


def robot_star(opts_t_ds):
    return robot(*opts_t_ds)


def robot(options, test, data_source):
    options['test'] = test
    options['outputdir'] += os.path.sep + test
    os.makedirs(options['outputdir'])
    stdout = os.path.join(options['outputdir'], test + ".out")
    stderr = os.path.join(options['outputdir'], test + ".err")
    with open(stdout, 'w') as stdout, open(stderr, 'w') as stderr:
        run(data_source, **options, stdout=stdout, stderr=stderr)


def parabot_cli(arguments, exit=True):
    """Command line execution entry point for running tests.
    :param arguments: Command line options and arguments as a list of strings.
    :param exit: If ``True``, call ``sys.exit`` with the return code denoting
        execution status, otherwise just return the rc. New in RF 3.0.1.
    Entry point used when running tests from the command line, but can also
    be used by custom scripts that execute tests. Especially useful if the
    script itself needs to accept same arguments as accepted by Robot Framework,
    because the script can just pass them forward directly along with the
    possible default values it sets itself.
    Example::
        from robot import run_cli
        # Run tests and return the return code.
        rc = run_cli(['--name', 'Example', 'tests.robot'], exit=False)
        # Run tests and exit to the system automatically.
        run_cli(['--name', 'Example', 'tests.robot'])
    See also the :func:`run` function that allows setting options as keyword
    arguments like ``name="Example"`` and generally has a richer API for
    programmatic test execution.
    """
    return Parabot().execute_cli(arguments, exit=exit)


if __name__ == '__main__':
    parabot_cli(sys.argv[1:])
