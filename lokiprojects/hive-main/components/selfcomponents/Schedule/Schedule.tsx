import React from 'react';
import { Clock, Users, Rocket, Coffee, Code, Trophy } from 'lucide-react';

const Schedule = () => {
  const scheduleData = [
    {
      day: 'Day 1',
      date: 'March 15',
      events: [
        {
          time: '9:00 AM',
          title: 'Registration & Check-in',
          description: 'Get your badges and welcome kit',
          icon: Clock
        },
        {
          time: '10:00 AM',
          title: 'Opening Ceremony',
          description: 'Welcome address and event kickoff',
          icon: Rocket
        },
        {
          time: '11:00 AM',
          title: 'Team Formation',
          description: 'Find your cosmic crew',
          icon: Users
        },
        {
          time: '12:00 PM',
          title: 'Lunch Break',
          description: 'Fuel up for the journey ahead',
          icon: Coffee
        }
      ]
    },
    {
      day: 'Day 2',
      date: 'March 16',
      events: [
        {
          time: '9:00 AM',
          title: 'Hacking Continues',
          description: 'Keep building and innovating',
          icon: Code
        },
        {
          time: '2:00 PM',
          title: 'Mentorship Sessions',
          description: 'Get guidance from experts',
          icon: Users
        }
      ]
    },
    {
      day: 'Day 3',
      date: 'March 17',
      events: [
        {
          time: '10:00 AM',
          title: 'Project Submissions',
          description: 'Submit your final projects',
          icon: Rocket
        },
        {
          time: '4:00 PM',
          title: 'Closing Ceremony',
          description: 'Awards and celebrations',
          icon: Trophy
        }
      ]
    }
  ];

  return (
    <section id="schedule" className="relative py-24 bg-black overflow-hidden">
      <div className="stars-1"></div>
      <div className="stars-2"></div>
      <div className="stars-3"></div>
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="section-heading text-center mb-16">Mission Timeline</h2>
        
        <div className="flex justify-center gap-4 mb-12">
          {scheduleData.map((day, index) => (
            <div key={index} className={`px-8 py-2 rounded-full ${index === 0 ? 'bg-white text-black' : 'bg-black/50 text-white'}`}>
              <span className="font-mono font-bold">{day.day}</span>
              <span className="ml-2 text-sm opacity-80">{day.date}</span>
            </div>
          ))}
        </div>

        <div className="relative">
          <div className="absolute left-1/2 top-0 bottom-0 w-px bg-white/20"></div>
          
          <div className="space-y-24">
            {scheduleData[0].events.map((event, index) => (
              <div key={index} className="relative">
                <div className="absolute left-1/2 -translate-x-1/2 -translate-y-1/2 w-12 h-12 bg-black/80 rounded-full border-2 border-white/20 flex items-center justify-center">
                  <event.icon className="w-6 h-6 text-white" />
                </div>
                
                <div className="grid grid-cols-2 gap-8">
                  <div className={`text-right ${index % 2 === 0 ? 'order-1' : 'order-2'}`}>
                    <h3 className="text-4xl font-mono font-bold text-white">{event.time}</h3>
                    <h4 className="text-2xl font-mono text-white mt-2">{event.title}</h4>
                    <p className="text-white/60 mt-1">{event.description}</p>
                  </div>
                  <div className={index % 2 === 0 ? 'order-2' : 'order-1'}></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default Schedule;