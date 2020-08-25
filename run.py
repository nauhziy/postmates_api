"""
This is the file that is invoked to start up a development server.
It gets a copy of the app from your package and runs it.
This won’t be used in production, but will be useful in development.
"""
# Run a test server.
from postmates import app


# ----------------------------------------------------------------------------#
#  Launch.
# ----------------------------------------------------------------------------#
# Default port:
if __name__ == '__main__':
    app.run(debug=True)


# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
