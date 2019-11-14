# generic_dependencycheck.py, Copyright (c) 2019, Nicholas Saparoff <nick.saparoff@gmail.com>: Original implementation

from phenome_core.core.base.base_dependencycheck import BaseDependencyCheck
from phenome_core.core.parsers.generic_argument_parser import GenericArgumentParser
from phenome_core.util.base_evaluator import BaseEvaluator
from phenome_core.core.base.logger import root_logger as logger

"""

Generic Dependency Check Extension. Extends a BaseDependency Check.

This is used by RelationModel dependency checks.

"""


class GenericDependencyCheck(BaseDependencyCheck):

    def __init__(self):
        super(GenericDependencyCheck, self).__init__()

    def finish(self):

        """
        Executes the Finish Logic for this check. Defaults to the Base Check functionality.

        Returns:
            None
        """

        super(GenericDependencyCheck, self).finish()

    def execute(self):

        """
        Executes a Generic Dependency Check for Relations.

        Returns:
            True if runs successfully.
        """

        # create the eval and parsers
        parser = GenericArgumentParser(self.args)

        # create local copies of variables that may be needed for parameter evaluation
        object = self.object
        relation = self.relation
        check_id = parser.get('id')

        # create the Param Evaluator
        evaluator = BaseEvaluator(check_id, locals())
        evaluator.set_parser(parser)

        has_attr_check = parser.get('relation_hasattr')
        if has_attr_check is not None:
            if hasattr(relation, has_attr_check) is False:
                return False

        related_model = parser.get('related_model')
        if related_model is None or related_model.upper() == 'ANY':
            # all good
            pass
        else:
            if relation.model.model != related_model:
                return False

        # determine if there is a trip for STATE 1
        self.state_1_match = evaluator.evaluate_as_boolean(parser.get('test_for_state_1'))

        # determine if there is a trip for STATE 2
        self.state_2_match = evaluator.evaluate_as_boolean(parser.get('test_for_state_2'))

        if self.state_1_match is False and self.state_2_match is False:
            return False

        if self.has_repeat_delay_enabled() is False:

            # set the repeat delay
            self.set_repeat_delay()

            action = None

            # we can go through with the set actions
            if self.state_1_match:
                self.message = evaluator.parse_and_evaluate('message_on_state_1')
                action = self.args.get('behavior_on_state_1')
            elif self.state_2_match:
                self.message = evaluator.parse_and_evaluate('message_on_state_2')
                action = self.args.get('behavior_on_state_2')

            if self.message:
                logger.debug(self.message)

            if action:
                evaluator.parse_and_evaluate(action)

            # we are here, so it ran, and was a success
            return True

        else:

            # fail due to delay
            return False
