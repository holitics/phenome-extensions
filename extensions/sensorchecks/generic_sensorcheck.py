# generic_sensorcheck.py, Copyright (c) 2019, Nicholas Saparoff <nick.saparoff@gmail.com>: Original implementation

from phenome_core.core.base.base_action import BaseAction
from phenome_core.core.base.healthscore import compute_health_score, add_health_score
from phenome_core.util import math_functions
from phenome_core.core.parsers.generic_argument_parser import GenericArgumentParser
from phenome_core.util.base_evaluator import BaseEvaluator
from phenome_core.core.base.logger import root_logger as logger
from phenome_core.core.helpers.string_helpers import str_to_bool

"""

Generic Check Extension. Extends a BaseAction.

This is used by ActionModel rules.

"""


class GenericCheck(BaseAction):

    def __init__(self):
        super(GenericCheck, self).__init__()

    def execute(self):

        """
        Executes a Generic Check for Actions.

        Returns:
            True if runs successfully.
        """

        object_results = {}
        has_error = False
        has_warning = False
        tested_alt_error = False
        healthscore = 0

        # some computed locals
        _result = None
        _result_avg = None
        _result_min = None
        _result_max = None

        # create the eval and parsers
        parser = GenericArgumentParser(self.args)

        # create local copies of variables that may be needed for parameter evaluation
        object = self.object
        results = self.results
        input = parser.get('input')
        check_id = parser.get('id')
        use_avg = parser.get('use_avg')
        error_timestamp = parser.get('error_timestamp')
        error_state_key = parser.get('error_state_key')
        alternate_error_check = parser.get('has_error_alt')

        if input is None:
            logger.error("No INPUT specified in args, check ID='{}'".format(check_id))
            return None
        try:
            if input.startswith("object."):
                # get the result directly from the object
                object_results = object.__getattribute__(input[7:])
            else:
                # get the result from the results
                object_results = self.results.get_result(self.object.id, input)
        except:
            pass

        if object_results is None:
            logger.error("No RESULTS found for input '{}', check ID='{}'".format(input, check_id))
            return False

        # First, error detection
        # is it a single value or is it a list?

        # TODO - add value_type to determine how to treat here. Right now, we assume float/numeric

        if isinstance(object_results, float) or isinstance(object_results, int):
            _result = object_results
        else:
            if isinstance(object_results, str):
                _result = float(object_results)
            else:
                # must be a list
                if len(object_results) > 0:
                    _result_avg = math_functions.get_average_of_list(object_results, 0)
                    _result_min = min(object_results)
                    _result_max = max(object_results)
                    if use_avg is not None and str_to_bool(use_avg):
                        _result = _result_avg
                    else:
                        # use the entire list as the result
                        _result = object_results

        if _result_min is None:
            _result_min = _result

        if _result_max is None:
            _result_max = _result

        if _result_avg is None:
            _result_avg = _result

        # create the Param Evaluator
        evaluator = BaseEvaluator(check_id, locals())
        evaluator.set_parser(parser)

        # get error and warning levels
        error_level = evaluator.parse_and_evaluate('error_level')
        warning_level = evaluator.parse_and_evaluate('warning_level')

        # get error and warning healthscores
        error_healthscore = evaluator.parse_and_evaluate('error_healthscore')
        warning_healthscore = evaluator.parse_and_evaluate('warning_healthscore')

        # determine if there is an error
        has_error = evaluator.evaluate_as_boolean(parser.get('has_error'))

        if has_error is False and alternate_error_check is not None:
            has_error = evaluator.evaluate_as_boolean(alternate_error_check)
            tested_alt_error = True

        if has_error is False:

            # determine if there is a warning
            has_warning = evaluator.evaluate_as_boolean(parser.get('has_warning'))
            if has_warning:
                self.has_warning = True
                self.error_message = evaluator.parse_and_evaluate('warning_message')
                healthscore = warning_healthscore
        else:

            self.has_error = True

            if tested_alt_error and parser.get('error_message_alt') is not None:
                self.error_message = evaluator.parse_and_evaluate('error_message_alt')
            else:
                self.error_message = evaluator.parse_and_evaluate('error_message')

            healthscore = error_healthscore

            try:
                if error_state_key is not None and self.object_states is not None:
                    # set the object state flag in the case object states are used
                    self.object_states.__setattr__(error_state_key,1)
            except:
                logger.error("Problem setting error_state_key '{}' for OBJECT ID={}".format(error_state_key, self.object.id))

        if self.results:

            if healthscore is None or healthscore == 0:
                if error_level and warning_level:
                    compute_health_score(self.object, self.results, _result_avg, warning_level, error_level)
            else:
                # add the pre-determined health score
                add_health_score(self.object, self.results, healthscore)

        # we are here, so it ran, and was a success
        return True

    def finish(self):

        """
        Executes Finish Method for Actions. Uses BaseAction as default. Handles Notifications, etc.

        Returns:
            None
        """

        super(GenericCheck, self).finish()