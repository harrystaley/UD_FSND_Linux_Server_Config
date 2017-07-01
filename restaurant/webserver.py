import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from database_setup import Base, Restaurant, MenuItem


__author__ = "Harry Staley <staleyh@gmail.com>"
__version__ = "1.0"

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class WebserverHandler(BaseHTTPRequestHandler):
    """ Class instantiates a web server to handle HTTP requests """
    def do_GET(self):
        """ handles the get requests for the web server """
        try:
            # renders the delete restaurant page
            if self.path.endswith("/delete"):
                resid = self.path.split("/")[2]
                template = "/resturants/%s/delete" % resid
                print "resid = %s" % resid
                dbq = session.query(Restaurant).filter_by(id=int(resid)
                                                          ).one()
                if not dbq == []:
                    self.send_response(200)
                    self.send_header('content-type', 'text/html')
                    self.end_headers()
                    name = dbq.name
                    print "name =%s" % name
                    output = ''
                    output += "<html><body>"
                    output += "<h2>Delete %s?</h2>" % name
                    output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/delete'>" % resid
                    output += "<input type='submit' value='Yes'>"
                    output += "</form>"
                    output += "</body></html>"
                    self.wfile.write(output)
                    print "The page %s has been rendered." % template
                    return
                else:
                    print "The page %s did not render." % template

            # renders the edit restaurant page
            if self.path.endswith("/edit"):
                resid = self.path.split("/")[2]
                template = "/resturants/%s/edit" % resid
                print "resid = %s" % resid
                dbq = session.query(Restaurant).filter_by(id=int(resid)
                                                          ).one()
                if not dbq == []:
                    self.send_response(200)
                    self.send_header('content-type', 'text/html')
                    self.end_headers()
                    name = dbq.name
                    print "name =%s" % name
                    output = ''
                    output += "<html><body>"
                    output += "<h2>Edit Restaurant</h2>"
                    output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'>" % resid
                    output += "<input name='RestaurantName' type='text' placeholder=%s>" % name
                    output += "<input type='submit' value='Submit'>"
                    output += "</form>"
                    output += "</body></html>"
                    self.wfile.write(output)
                    print "The page %s has been rendered." % template
                    return
                else:
                    print "The page %s did not render." % template

            # renders the /restaurants/new page
            if self.path.endswith("/new"):
                self.send_response(200)
                self.send_header('content-type', 'text/html')
                self.end_headers()
                template = "/resturants/new"
                output = ''
                output += "<html><body>"
                output += "<h2>New Restaurant</h2>"
                output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>"
                output += "<input name='RestaurantName' type='text'>"
                output += "<input type='submit' value='Submit'>"
                output += "</form>"
                output += "</body></html>"
                self.wfile.write(output)
                print "The page %s has been rendered." % template
                return

            # renders the /restaurants page
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('content-type', 'text/html')
                self.end_headers()
                template = "/resturants"
                restaurants = session.query(Restaurant).all()
                output = ''
                output += "<html><body>"
                output += "Restaurants"
                output += "<br><br>"
                output += "<a href='/restaurants/new'>New Restaurant</a>"
                output += "<br>"
                for restaurant in restaurants:
                    output += restaurant.name
                    output += "<a href='/restaurants/%s/edit'> Edit</a>" % restaurant.id
                    output += "<a href='/restaurants/%s/delete'> Delete</a>" % restaurant.id
                    output += "<br><br>"

                output += "</body></html>"
                self.wfile.write(output)
                print "The page %s has been rendered." % template
                return

        except IOError:
            self.send_error(404, "File not found %s" % self.path)

    def do_POST(self):
        """ Handles the post requests for the HTTP server """
        try:
            # Handles the post request from /restaurants/new
            if self.path.endswith("/new"):
                ctype, pdict = cgi.parse_header(self.headers
                                                .getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    restaurantform = fields.get('RestaurantName')

                newrestaurant = Restaurant(name=restaurantform[0])
                session.add(newrestaurant)
                session.commit()

                self.send_response(301)
                self.send_header('content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()
                return

            # Handles the post request from the edit page
            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers
                                                .getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    restaurantform = fields.get('RestaurantName')
                resid = self.path.split("/")[2]
                restaurant = session.query(Restaurant).filter_by(id=resid
                                                                 ).one()
                if restaurant:
                    restaurant.name = restaurantform[0]
                session.add(restaurant)
                session.commit()

                self.send_response(301)
                self.send_header('content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()
                return

            # Handles the post request from the delete page
            if self.path.endswith("/delete"):
                resid = self.path.split("/")[2]
                restaurant = session.query(Restaurant).filter_by(id=resid
                                                                 ).one()
                session.delete(restaurant)
                session.commit()

                self.send_response(301)
                self.send_header('content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()
                return
        except:
            pass


def main():
    """ Main class for the web server responses from/to the user """
    try:
        port = 8080
        server = HTTPServer(('', port), WebserverHandler)
        print "Server running on port %s press ctrl+c to stop..." % port
        server.serve_forever()
    except KeyboardInterrupt:
        print "ctrl+c entered, stopping web server..."
        server.socket.close()


if __name__ == '__main__':
    main()
