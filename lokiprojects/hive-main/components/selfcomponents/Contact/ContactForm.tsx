import React from 'react';
import { Send } from 'lucide-react';

const ContactForm = () => {
  return (
    <form className="space-y-6">
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-violet-200">
          Name
        </label>
        <input
          type="text"
          id="name"
          className="mt-1 block w-full rounded-md bg-indigo-900/30 border-violet-500 text-violet-100 placeholder-violet-400"
          placeholder="Your name"
        />
      </div>
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-violet-200">
          Email
        </label>
        <input
          type="email"
          id="email"
          className="mt-1 block w-full rounded-md bg-indigo-900/30 border-violet-500 text-violet-100 placeholder-violet-400"
          placeholder="you@example.com"
        />
      </div>
      <div>
        <label htmlFor="message" className="block text-sm font-medium text-violet-200">
          Message
        </label>
        <textarea
          id="message"
          rows={4}
          className="mt-1 block w-full rounded-md bg-indigo-900/30 border-violet-500 text-violet-100 placeholder-violet-400"
          placeholder="Your message"
        />
      </div>
      <button
        type="submit"
        className="w-full flex justify-center items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-violet-600 hover:bg-violet-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-violet-500"
      >
        Send Message
        <Send className="ml-2 h-4 w-4" />
      </button>
    </form>
  );
};

export default ContactForm;