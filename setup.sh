#!/usr/bin/env bash

# exit when any command fails
set -o errexit

## Install dependencies via pip
pip install -r requirements.txt

## Run migration just in case
python manage.py migrate

{loading ? (
            <button
              className="bg-gradient-to-r from-gray-900 to-gray-900 py-3 px-4 mx-3 rounded-md text-white"
              disabled
            >
              Loading...
            </button>
          ) : (
            <button
              onClick={handleStartForFree}
              className="bg-gradient-to-r from-gray-900 to-gray-900 py-3 px-4 mx-3 rounded-md text-white"
            >
              Start for free
            </button>
          )}

            const handleStartForFree = () => {
    setLoading(true); // Set loading to true
    setTimeout(() => {
      navigate("/api/signup"); // Navigate after a short delay
      setLoading(false); // Reset loading (optional if navigation happens quickly)
    }, 1500); // Simulate a delay
  };