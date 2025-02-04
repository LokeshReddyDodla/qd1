"use client"
import React from 'react';
import ContactForm from './ContactForm';
import { MapPin, Mail, Phone } from 'lucide-react';

const Contact = () => {
  return (
    <section id="contact" className="py-24 bg-black">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-extrabold text-white sm:text-4xl">
            Get in Touch
          </h2>
          <p className="mt-4 text-xl text-violet-200">
            Have questions? We're here to help
          </p>
        </div>
        <div className="grid gap-8 md:grid-cols-2">
          <div>
            <div className="space-y-8">
              <div className="flex items-start space-x-4">
                <MapPin className="h-6 w-6 text-violet-400" />
                <div>
                  <h3 className="text-lg font-medium text-white">Location</h3>
                  <p className="mt-1 text-violet-200">
                    Tech Hub Convention Center<br />
                    123 Innovation Street<br />
                    San Francisco, CA 94105
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-4">
                <Mail className="h-6 w-6 text-violet-400" />
                <div>
                  <h3 className="text-lg font-medium text-white">Email</h3>
                  <p className="mt-1 text-violet-200">
                    contact@web3frontier.com
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-4">
                <Phone className="h-6 w-6 text-violet-400" />
                <div>
                  <h3 className="text-lg font-medium text-white">Phone</h3>
                  <p className="mt-1 text-violet-200">
                    +1 (555) 123-4567
                  </p>
                </div>
              </div>
            </div>
          </div>
          <div>
            <ContactForm />
          </div>
        </div>
      </div>
    </section>
  );
};

export default Contact;