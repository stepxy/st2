from st2common.persistence.action import Action
from st2common.persistence.reactor import Trigger
from st2common.models.db import action, reactor
from tests import FunctionalTest

ACTION = action.ActionDB()
ACTION.name = 'st2.test.action1'
ACTION.description = ''
ACTION.enabled = True
ACTION.artifact_path = '/tmp/action.py'
ACTION.entry_point = ''
ACTION.runner_type = 'python'
ACTION.parameter_names = ['p1', 'p2', 'p3']

TRIGGER = reactor.TriggerDB()
TRIGGER.name = 'st2.test.trigger1'
TRIGGER.description = ''
TRIGGER.payload_info = ['tp1', 'tp2', 'tp3']
TRIGGER.trigger_source = None

RULE_1 = {
    'enabled': True,
    'name': 'st2.test.rule1',
    'trigger_type': {
        'name': 'st2.test.trigger1'
    },
    'rule_data': {
        'k1': 'v1'
    },
    'criteria': {
        't1_p': {
            'pattern': 't1_p_v',
            'type': 'equals'
        }
    },
    'action': {
        'type': {
            'name': 'st2.test.action'
        },
        'mapping': {
            'ip2': '{{rule.k1}}',
            'ip1': '{{trigger.t1_p}}'
        }
    },
    'id': '23',
    'description': ''
}


class TestRuleController(FunctionalTest):

    def setUp(self):
        ACTION.id = None
        Action.add_or_update(ACTION)
        TRIGGER.id = None
        Trigger.add_or_update(TRIGGER)

    def tearDown(self):
        Action.delete(ACTION)
        Trigger.delete(TRIGGER)

    def test_get_all(self):
        resp = self.app.get('/rules')
        self.assertEqual(resp.status_int, 200)

    def test_get_one(self):
        post_resp = self.__do_post(RULE_1)
        rule_id = self.__get_rule_id(post_resp)
        get_resp = self.__do_get_one(rule_id)
        self.assertEquals(get_resp.status_int, 200)
        self.assertEquals(self.__get_rule_id(get_resp), rule_id)
        self.__do_delete(rule_id)

    def test_get_one_fail(self):
        resp = self.app.get('/rules/1', expect_errors=True)
        self.assertEqual(resp.status_int, 404)

    def test_post_delete(self):
        post_resp = self.__do_post(RULE_1)
        self.assertEquals(post_resp.status_int, 201)
        self.__do_delete(self.__get_rule_id(post_resp))

    def test_put(self):
        post_resp = self.__do_post(RULE_1)
        update_input = post_resp.json
        update_input['enabled'] = not update_input['enabled']
        put_resp = self.__do_put(self.__get_rule_id(post_resp), update_input)
        self.assertEquals(put_resp.status_int, 200)
        self.__do_delete(self.__get_rule_id(put_resp))

    def test_put_fail(self):
        post_resp = self.__do_post(RULE_1)
        update_input = post_resp.json
        # If the id in the URL is incorrect the update will fail since id in the body is ignored.
        put_resp = self.__do_put(1, update_input)
        self.assertEquals(put_resp.status_int, 404)
        self.__do_delete(self.__get_rule_id(post_resp))

    def test_delete(self):
        post_resp = self.__do_post(RULE_1)
        del_resp = self.__do_delete(self.__get_rule_id(post_resp))
        self.assertEquals(del_resp.status_int, 204)

    @staticmethod
    def __get_rule_id(resp):
        return resp.json['id']

    def __do_get_one(self, rule_id):
        return self.app.get('/rules/%s' % rule_id)

    def __do_post(self, rule):
        return self.app.post_json('/rules', rule)

    def __do_put(self, rule_id, rule):
        return self.app.put_json('/rules/%s' % rule_id, rule, expect_errors=True)

    def __do_delete(self, rule_id):
        return self.app.delete('/rules/%s' % rule_id)
