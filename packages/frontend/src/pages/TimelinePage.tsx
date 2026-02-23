import React from 'react';
import { useQuery } from 'react-query';
import { ClockIcon, CalendarIcon, MapPinIcon } from '@heroicons/react/24/outline';
import { eventsAPI } from '../services/api';
import { format } from 'date-fns';

export const TimelinePage: React.FC = () => {
  const { data: timeline, isLoading } = useQuery(
    'timeline',
    () => eventsAPI.getTimeline().then(res => res.data),
  );

  const { data: events } = useQuery(
    'events',
    () => eventsAPI.getAll().then(res => res.data),
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Timeline</h1>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Family Timeline</h2>
        {timeline?.length > 0 ? (
          <div className="relative">
            <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200"></div>
            <div className="space-y-8">
              {timeline.map((event: any, index: number) => (
                <div key={event.id} className="relative flex items-start">
                  <div className="flex items-center justify-center w-16 h-16 bg-white border-4 border-indigo-500 rounded-full">
                    <ClockIcon className="h-6 w-6 text-indigo-500" />
                  </div>
                  <div className="ml-6 flex-1">
                    <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">{event.event_type}</h3>
                        <span className="text-sm text-gray-500">
                          {event.event_date ? format(new Date(event.event_date), 'MMM dd, yyyy') : 'Date unknown'}
                        </span>
                      </div>
                      <p className="text-gray-700 mb-2">{event.description}</p>
                      {event.event_place && (
                        <div className="flex items-center text-sm text-gray-500">
                          <MapPinIcon className="h-4 w-4 mr-1" />
                          {event.event_place}
                        </div>
                      )}
                      {event.individual_name && (
                        <div className="mt-2">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {event.individual_name}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="text-center py-12">
            <ClockIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No events found in timeline</p>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Event Statistics</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Total Events</span>
              <span className="font-semibold">{events?.length || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Births</span>
              <span className="font-semibold">
                {events?.filter((e: any) => e.event_type === 'BIRTH').length || 0}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Marriages</span>
              <span className="font-semibold">
                {events?.filter((e: any) => e.event_type === 'MARR').length || 0}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Deaths</span>
              <span className="font-semibold">
                {events?.filter((e: any) => e.event_type === 'DEAT').length || 0}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Events</h3>
          <div className="space-y-2">
            {events?.slice(0, 5).map((event: any) => (
              <div key={event.id} className="flex items-center justify-between py-2 border-b border-gray-100">
                <div>
                  <p className="text-sm font-medium text-gray-900">{event.event_type}</p>
                  <p className="text-xs text-gray-500">
                    {event.event_date ? format(new Date(event.event_date), 'MMM dd, yyyy') : 'Unknown date'}
                  </p>
                </div>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  event.event_type === 'BIRTH' ? 'bg-green-100 text-green-800' :
                  event.event_type === 'MARR' ? 'bg-blue-100 text-blue-800' :
                  event.event_type === 'DEAT' ? 'bg-gray-100 text-gray-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {event.event_type}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Timeline Filters</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Event Type</label>
              <select className="w-full border border-gray-300 rounded-lg px-3 py-2">
                <option value="">All Events</option>
                <option value="BIRTH">Births</option>
                <option value="MARR">Marriages</option>
                <option value="DEAT">Deaths</option>
                <option value="EVEN">Other Events</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Date Range</label>
              <input
                type="date"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 mb-2"
                placeholder="From"
              />
              <input
                type="date"
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
                placeholder="To"
              />
            </div>
            <button className="w-full bg-indigo-600 text-white rounded-lg px-4 py-2 hover:bg-indigo-700">
              Apply Filters
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
