import unittest
from pathlib import Path
import time
import os
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from core.queue_manager import ConversionQueue, QueueItem

class TestQueueManager(unittest.TestCase):
    def setUp(self):
        self.updates = 0
        def on_update():
            self.updates += 1
            
        def dummy_worker(item):
            time.sleep(0.1) # Simulate work
            
        self.queue_manager = ConversionQueue(worker_func=dummy_worker, on_queue_update=on_update)
        
    def test_add_item_starts_worker(self):
        self.assertFalse(self.queue_manager.is_running)
        self.queue_manager.add_item(Path("test.pdf"), "pdf2word")
        self.assertTrue(self.queue_manager.is_running)
        self.assertEqual(len(self.queue_manager.items), 1)
        
        # Wait for worker to finish
        time.sleep(0.3)
        self.assertFalse(self.queue_manager.is_running)
        self.assertEqual(self.queue_manager.items[0].status, "success")
        self.assertGreater(self.updates, 0)

    def test_clear_completed(self):
        # Manually set items
        item1 = QueueItem(Path("f1.pdf"), "pdf2word", status="success")
        item2 = QueueItem(Path("f2.pdf"), "pdf2word", status="failed")
        item3 = QueueItem(Path("f3.pdf"), "pdf2word", status="running")
        item4 = QueueItem(Path("f4.pdf"), "pdf2word", status="pending")
        
        self.queue_manager.items = [item1, item2, item3, item4]
        self.queue_manager.clear_completed()
        
        # Only running and pending should remain
        self.assertEqual(len(self.queue_manager.items), 2)
        statuses = [item.status for item in self.queue_manager.items]
        self.assertIn("running", statuses)
        self.assertIn("pending", statuses)

if __name__ == '__main__':
    unittest.main()
