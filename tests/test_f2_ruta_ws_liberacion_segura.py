"""Tests B sintéticos: no implican PPSSPP ni fotogramas reales."""
import json
import unittest
from tools.f2_ruta_ws_liberacion_segura import (SCHEMA, BUTTONS, RELEASE_ALL, validate_steps, execute)


class Conn:
    def __init__(self):
        self.messages = []
    def send(self, payload):
        self.messages.append(json.loads(payload))


class Fake:
    def __init__(self, fail_press=False, fail_release=False, stepping=False):
        self.conn = Conn()
        self.events = []
        self.fail_press, self.fail_release, self.stepping = fail_press, fail_release, stepping
    def request(self, event, **kwargs):
        self.events.append((event, kwargs))
        if event == 'cpu.status':
            return {'event': event, 'stepping': self.stepping}
        if event == 'input.buttons.press' and self.fail_press:
            raise TimeoutError('press frame timeout')
        if event == 'input.buttons.send' and self.fail_release:
            raise TimeoutError('release frame timeout')
        return {'event': event}


class TestRoute(unittest.TestCase):
    def setUp(self):
        self.steps = [{'kind':'checkpoint', 'label':'START SKIP Cheery Girl'},
                      {'kind':'press', 'button':'start', 'frames':8}]
    def test_valid(self):
        self.assertEqual(validate_steps({'schema':SCHEMA,'steps':self.steps}),self.steps)
    def test_reject_without_checkpoint(self):
        with self.assertRaises(ValueError): validate_steps({'schema':SCHEMA,'steps':[self.steps[1]]})
    def test_reject_unknown_action(self):
        with self.assertRaises(ValueError): validate_steps({'schema':SCHEMA,'steps':[{'kind':'shell','cmd':'rm -rf'}]})
    def test_reject_invalid_frames(self):
        for value in (0,121,-1,True,'8'):
            with self.subTest(value=value),self.assertRaises(ValueError):
                validate_steps({'schema':SCHEMA,'steps':[self.steps[0],dict(self.steps[1],frames=value)]})
    def test_reject_invalid_button(self):
        with self.assertRaises(ValueError):
            validate_steps({'schema':SCHEMA,'steps':[self.steps[0],dict(self.steps[1],button='jump')]})
    def test_reject_unsafe_label(self):
        with self.assertRaises(ValueError):
            validate_steps({'schema':SCHEMA,'steps':[dict(self.steps[0],label='</bad>')]})
    def test_reject_extra_fields(self):
        with self.assertRaises(ValueError):
            validate_steps({'schema':SCHEMA,'steps':[dict(self.steps[0],eval='true')]})
    def test_reject_empty(self):
        with self.assertRaises(ValueError):validate_steps({'schema':SCHEMA,'steps':[]})
    def test_reject_unknown_schema(self):
        with self.assertRaises(ValueError):validate_steps({'schema':'other','steps':self.steps})
    def test_button_names_actual(self):
        self.assertIn('ltrigger',BUTTONS);self.assertNotIn('l',BUTTONS)
        self.assertEqual(set(RELEASE_ALL),set(BUTTONS));self.assertTrue(all(v is False for v in RELEASE_ALL.values()))
    def test_pass_and_release(self):
        client=Fake();out=execute(client,self.steps,lambda _: True)
        self.assertTrue(out['completed']);self.assertTrue(out['explicit_release_acknowledged'])
        self.assertEqual([e for e,_ in client.events if e=='input.buttons.press'].count('input.buttons.press'),1)
        self.assertGreaterEqual(sum(1 for e,_ in client.events if e=='input.buttons.send'),3)
    def test_press_timeout_release_attempted(self):
        client=Fake(fail_press=True);out=execute(client,self.steps,lambda _: True)
        self.assertFalse(out['completed']);self.assertTrue(out['explicit_release_acknowledged'])
        self.assertIn('press frame timeout',out['error'])
        self.assertGreaterEqual(sum(1 for e,_ in client.events if e=='input.buttons.send'),3)
        self.assertEqual(len(client.conn.messages),1)
    def test_release_timeout_fails_closed(self):
        client=Fake(fail_release=True);out=execute(client,self.steps,lambda _: True)
        self.assertFalse(out['completed']);self.assertFalse(out['explicit_release_acknowledged'])
    def test_cpu_paused_no_press(self):
        client=Fake(stepping=True);out=execute(client,self.steps,lambda _: True)
        self.assertFalse(out['completed']);self.assertFalse(any(e=='input.buttons.press' for e,_ in client.events))
    def test_checkpoint_not_confirmed(self):
        client=Fake();out=execute(client,self.steps,lambda _: False)
        self.assertFalse(out['completed']);self.assertFalse(any(e=='input.buttons.press' for e,_ in client.events))
    def test_complete_does_not_claim_scene(self):
        client=Fake();out=execute(client,self.steps,lambda _: True)
        self.assertFalse(out['tuika_runtime_proven']);self.assertFalse(out['capture_synchronized'])
    def test_all_release_requests_are_false(self):
        client=Fake();execute(client,self.steps,lambda _: True)
        for e,kwargs in client.events:
            if e=='input.buttons.send':self.assertEqual(kwargs['buttons'],RELEASE_ALL)
        for data in client.conn.messages:self.assertEqual(data['buttons'],RELEASE_ALL)


if __name__=='__main__':unittest.main()
