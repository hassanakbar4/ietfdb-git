import debug                            # pyflakes:ignore

from django.core.urlresolvers import reverse

from ietf.group.models import Group
from ietf.meeting.models import Meeting, Session
from ietf.meeting.test_data import make_meeting_test_data
from ietf.person.models import Person
from ietf.utils.test_data import make_test_data
from ietf.utils.test_utils import TestCase

SECR_USER='secretary'

class MainTestCase(TestCase):
    def test_main(self):
        "Main Test"
        make_test_data()
        url = reverse('proceedings')
        self.client.login(username="secretary", password="secretary+password")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

class RecordingsTestCase(TestCase):
    def test_page(self):
        make_test_data()
        meeting = Meeting.objects.first()
        url = reverse('proceedings_recording', kwargs={'meeting_num':meeting.number})
        self.client.login(username="secretary", password="secretary+password")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    def test_post(self):
        make_meeting_test_data()
        meeting = Meeting.objects.first()
        group = Group.objects.get(acronym='mars')
        #session = Session.objects.create(group=group,
        #                       requested_by=Person.objects.get(name="(System)"),
        #                       meeting=meeting,
        #                       status_id='sched')
        # need ss and timeslot
        session = Session.objects.filter(meeting=meeting,group=group,status__in=('sched','schedw')).first()
        url = reverse('proceedings_recording', kwargs={'meeting_num':meeting.number})
        data = dict(group=group.acronym,external_url='http://youtube.com/xyz',session=session.pk)
        self.client.login(username="secretary", password="secretary+password")
        response = self.client.post(url,data,follow=True)
        self.assertEqual(response.status_code, 200)
        print response.content
        self.failUnless(group.acronym in response.content)
        
    #def test_edit(self):