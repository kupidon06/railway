"""
Management command to seed the database with demo data.

Usage: python manage.py seed_data [--clear]
"""
import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from railway_core.models import Node, Track, Train, Schedule, Event, Incident


class Command(BaseCommand):
    help = 'Seed the database with demo railway data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            self.clear_data()

        self.stdout.write(self.style.SUCCESS('Starting data seeding...'))

        # Seed nodes
        nodes = self.seed_nodes()
        self.stdout.write(self.style.SUCCESS(f'Created {len(nodes)} nodes'))

        # Seed tracks
        tracks = self.seed_tracks(nodes)
        self.stdout.write(self.style.SUCCESS(f'Created {len(tracks)} tracks'))

        # Seed trains
        trains = self.seed_trains()
        self.stdout.write(self.style.SUCCESS(f'Created {len(trains)} trains'))

        # Seed schedules
        schedules = self.seed_schedules(trains, nodes, tracks)
        self.stdout.write(self.style.SUCCESS(f'Created {len(schedules)} schedules'))

        # Seed events
        events = self.seed_events(trains, nodes, tracks)
        self.stdout.write(self.style.SUCCESS(f'Created {len(events)} events'))

        # Seed incidents
        incidents = self.seed_incidents(nodes, tracks, trains)
        self.stdout.write(self.style.SUCCESS(f'Created {len(incidents)} incidents'))

        self.stdout.write(self.style.SUCCESS('\n✓ Database seeded successfully!'))
        self.stdout.write(self.style.SUCCESS(f'Total: {len(nodes)} nodes, {len(tracks)} tracks, {len(trains)} trains'))

    def clear_data(self):
        """Clear all existing data."""
        Event.objects.all().delete()
        Schedule.objects.all().delete()
        Incident.objects.all().delete()
        Train.objects.all().delete()
        Track.objects.all().delete()
        Node.objects.all().delete()

    def seed_nodes(self):
        """Create demo nodes (stations)."""
        nodes_data = [
            {
                'code': 'PARIS_NORD',
                'name': 'Paris Gare du Nord',
                'latitude': 48.8809,
                'longitude': 2.3553,
                'capacity': 30,
                'node_type': Node.NodeType.STATION,
                'timezone': 'Europe/Paris'
            },
            {
                'code': 'LYON_PART_DIEU',
                'name': 'Lyon Part-Dieu',
                'latitude': 45.7607,
                'longitude': 4.8595,
                'capacity': 25,
                'node_type': Node.NodeType.STATION,
                'timezone': 'Europe/Paris'
            },
            {
                'code': 'MARSEILLE_ST_CHARLES',
                'name': 'Marseille Saint-Charles',
                'latitude': 43.3025,
                'longitude': 5.3803,
                'capacity': 20,
                'node_type': Node.NodeType.STATION,
                'timezone': 'Europe/Paris'
            },
            {
                'code': 'LILLE_EUROPE',
                'name': 'Lille Europe',
                'latitude': 50.6386,
                'longitude': 3.0754,
                'capacity': 15,
                'node_type': Node.NodeType.STATION,
                'timezone': 'Europe/Paris'
            },
            {
                'code': 'BORDEAUX_ST_JEAN',
                'name': 'Bordeaux Saint-Jean',
                'latitude': 44.8261,
                'longitude': -0.5558,
                'capacity': 18,
                'node_type': Node.NodeType.STATION,
                'timezone': 'Europe/Paris'
            }
        ]

        nodes = []
        for data in nodes_data:
            node, created = Node.objects.get_or_create(
                code=data['code'],
                defaults=data
            )
            nodes.append(node)

        return nodes

    def seed_tracks(self, nodes):
        """Create tracks for each node."""
        tracks = []
        directions = [Track.Direction.INBOUND, Track.Direction.OUTBOUND, Track.Direction.BIDIRECTIONAL]

        for node in nodes:
            track_count = node.capacity
            for i in range(1, track_count + 1):
                track_code = f"{node.code}_T{i}"
                track, created = Track.objects.get_or_create(
                    code=track_code,
                    defaults={
                        'name': f'Track {i}',
                        'node': node,
                        'track_number': i,
                        'length_meters': random.randint(400, 800),
                        'max_speed_kmh': random.choice([80, 120, 160]),
                        'direction': random.choice(directions),
                        'status': Track.Status.OPERATIONAL
                    }
                )
                tracks.append(track)

        return tracks

    def seed_trains(self):
        """Create demo trains."""
        trains_data = [
            {'train_number': 'TGV8501', 'train_type': Train.TrainType.TGV, 'operator': 'SNCF', 'capacity': 500, 'length': 200.0, 'max_speed': 320},
            {'train_number': 'TGV8502', 'train_type': Train.TrainType.TGV, 'operator': 'SNCF', 'capacity': 500, 'length': 200.0, 'max_speed': 320},
            {'train_number': 'TGV8503', 'train_type': Train.TrainType.TGV, 'operator': 'SNCF', 'capacity': 500, 'length': 200.0, 'max_speed': 320},
            {'train_number': 'IC4711', 'train_type': Train.TrainType.INTERCITE, 'operator': 'SNCF', 'capacity': 350, 'length': 150.0, 'max_speed': 200},
            {'train_number': 'IC4712', 'train_type': Train.TrainType.INTERCITE, 'operator': 'SNCF', 'capacity': 350, 'length': 150.0, 'max_speed': 200},
            {'train_number': 'TER8601', 'train_type': Train.TrainType.TER, 'operator': 'SNCF', 'capacity': 200, 'length': 80.0, 'max_speed': 160},
            {'train_number': 'TER8602', 'train_type': Train.TrainType.TER, 'operator': 'SNCF', 'capacity': 200, 'length': 80.0, 'max_speed': 160},
            {'train_number': 'TER8603', 'train_type': Train.TrainType.TER, 'operator': 'SNCF', 'capacity': 200, 'length': 80.0, 'max_speed': 160},
            {'train_number': 'TER8604', 'train_type': Train.TrainType.TER, 'operator': 'SNCF', 'capacity': 200, 'length': 80.0, 'max_speed': 160},
            {'train_number': 'CARGO5001', 'train_type': Train.TrainType.CARGO, 'operator': 'SNCF Fret', 'capacity': None, 'length': 400.0, 'max_speed': 100},
            {'train_number': 'CARGO5002', 'train_type': Train.TrainType.CARGO, 'operator': 'SNCF Fret', 'capacity': None, 'length': 400.0, 'max_speed': 100},
        ]

        trains = []
        for data in trains_data:
            train, created = Train.objects.get_or_create(
                train_number=data['train_number'],
                defaults={
                    'train_type': data['train_type'],
                    'operator': data['operator'],
                    'capacity_passengers': data['capacity'],
                    'length_meters': data['length'],
                    'max_speed_kmh': data['max_speed']
                }
            )
            trains.append(train)

        return trains

    def seed_schedules(self, trains, nodes, tracks):
        """Create schedules for trains."""
        schedules = []
        now = timezone.now()
        statuses = [Schedule.Status.SCHEDULED, Schedule.Status.ON_TIME, Schedule.Status.DELAYED]

        # Create schedules for the next 24 hours
        for train in trains[:8]:  # Only schedule passenger trains
            # Each train visits 3-4 nodes
            visited_nodes = random.sample(nodes, random.randint(3, 4))

            current_time = now + timedelta(hours=random.randint(0, 12))

            for i, node in enumerate(visited_nodes):
                # Get available tracks at this node
                available_tracks = list(node.tracks.filter(status=Track.Status.OPERATIONAL)[:5])

                if not available_tracks:
                    continue

                track = random.choice(available_tracks)

                # Calculate arrival and departure
                arrival = current_time
                departure = arrival + timedelta(minutes=random.randint(5, 15))

                # Sometimes add delays
                status = random.choice(statuses)
                delay = 0
                actual_arrival = None
                actual_departure = None

                if status == Schedule.Status.DELAYED:
                    delay = random.randint(5, 30)
                    if current_time < now:
                        actual_arrival = arrival + timedelta(minutes=delay)

                schedule, created = Schedule.objects.get_or_create(
                    train=train,
                    node=node,
                    scheduled_arrival=arrival,
                    defaults={
                        'track': track,
                        'scheduled_departure': departure,
                        'actual_arrival': actual_arrival,
                        'status': status,
                        'delay_minutes': delay,
                        'notes': f'Stop {i+1} of {len(visited_nodes)}'
                    }
                )
                schedules.append(schedule)

                # Next stop is 1-2 hours later
                current_time = departure + timedelta(hours=random.uniform(0.5, 2))

        return schedules

    def seed_events(self, trains, nodes, tracks):
        """Create sample events."""
        events = []
        now = timezone.now()

        event_types = [
            Event.EventType.ARRIVAL,
            Event.EventType.DEPARTURE,
            Event.EventType.DELAY,
            Event.EventType.TRACK_CHANGE
        ]

        severities = [Event.Severity.INFO, Event.Severity.WARNING]

        # Create events for the last 24 hours
        for _ in range(50):
            event_time = now - timedelta(hours=random.randint(0, 24))
            train = random.choice(trains)
            node = random.choice(nodes)
            track = random.choice(list(node.tracks.all()[:5]))
            event_type = random.choice(event_types)

            descriptions = {
                Event.EventType.ARRIVAL: f'{train.train_number} arrived at {node.name}',
                Event.EventType.DEPARTURE: f'{train.train_number} departed from {node.name}',
                Event.EventType.DELAY: f'{train.train_number} delayed by {random.randint(5, 20)} minutes',
                Event.EventType.TRACK_CHANGE: f'{train.train_number} changed to track {track.track_number}'
            }

            event = Event.objects.create(
                timestamp=event_time,
                event_type=event_type,
                train=train,
                node=node,
                track=track,
                severity=random.choice(severities),
                description=descriptions[event_type],
                metadata={'source': 'seed_data'}
            )
            events.append(event)

        return events

    def seed_incidents(self, nodes, tracks, trains):
        """Create sample incidents."""
        incidents = []
        now = timezone.now()

        incident_data = [
            {
                'title': 'Signal Failure at Paris Nord',
                'description': 'Technical issue with signaling system causing delays',
                'incident_type': Incident.IncidentType.TECHNICAL,
                'severity': Incident.Severity.MEDIUM,
                'node': nodes[0],
                'status': Incident.Status.MONITORING
            },
            {
                'title': 'Track Maintenance at Lyon',
                'description': 'Scheduled maintenance on tracks 3 and 4',
                'incident_type': Incident.IncidentType.TECHNICAL,
                'severity': Incident.Severity.LOW,
                'node': nodes[1],
                'status': Incident.Status.ACTIVE
            }
        ]

        for data in incident_data:
            started_at = now - timedelta(hours=random.randint(1, 12))

            incident = Incident.objects.create(
                title=data['title'],
                description=data['description'],
                incident_type=data['incident_type'],
                severity=data['severity'],
                node=data['node'],
                started_at=started_at,
                status=data['status']
            )

            # Add some affected tracks
            node_tracks = list(data['node'].tracks.all()[:3])
            if node_tracks:
                incident.affected_tracks.add(*node_tracks)

            # Add some affected trains
            affected_trains = random.sample(trains, min(3, len(trains)))
            incident.affected_trains.add(*affected_trains)

            incidents.append(incident)

        return incidents
