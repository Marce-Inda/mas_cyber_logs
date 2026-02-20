import unittest
from environment import CyberEnvironment
from agents import UserAgent, SysAdminAgent, AttackerAgent, CEOAgent

class TestMASEnvironmentsAndAgents(unittest.TestCase):
    
    def setUp(self):
        self.env = CyberEnvironment()
        self.user = UserAgent(name="TestUser")
        self.sysadmin = SysAdminAgent(name="TestAdmin")
        self.attacker = AttackerAgent(name="TestHacker")
        self.ceo = CEOAgent(name="TestCEO")
        self.agents = [self.user, self.sysadmin, self.attacker, self.ceo]

    def test_environment_initial_state(self):
        self.assertEqual(self.env.state["suspicious_events"], 0)
        self.assertEqual(self.env.state["compromised_hosts"], 0)
        self.assertEqual(len(self.env.logs), 0)

    def test_agent_roles(self):
        self.assertEqual(self.user.role, "Employee")
        self.assertEqual(self.sysadmin.role, "SysAdmin")
        self.assertEqual(self.attacker.role, "Attacker")
        self.assertEqual(self.ceo.role, "CEO")

    def test_environment_step(self):
        # Force agents to use mock_act by bypassing LLM probability for absolute testing
        for agent in self.agents:
            agent.llm_rate = 0.0
            
        self.env.step(self.agents)
        self.assertEqual(len(self.env.logs), 4)

    def test_attacker_increases_suspicious_state(self):
        self.attacker.llm_rate = 0.0
        # The attacker mock_act has 3/4 chances of suspicious or compromise event
        # We will mock the mock_act temporarily to ensure a suspicious event
        original_mock_act = self.attacker.mock_act
        self.attacker.mock_act = lambda state: {
            "agent": "TestHacker", "role": "Attacker",
            "action": "port_scan", "event_type": "suspicious", "details": "test"
        }
        
        self.env.step([self.attacker])
        self.assertEqual(self.env.state["suspicious_events"], 1)
        self.attacker.mock_act = original_mock_act # Restore

if __name__ == '__main__':
    unittest.main()
