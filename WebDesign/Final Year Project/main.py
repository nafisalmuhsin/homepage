# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
    port = 5000,

#Below is only for enabling https when hosting on the Unbuntu server where a certificate and key are enabled.
#I've left this for my markers to know what i used for https
#remove hashtags to test

#if __name__ == '__main__':
#    app.run(
#    host ='0.0.0.0',
#    port = 5000,
#    ssl_context = ('certs/cert.pem', 'certs/key.pem'),
#    debug = True
#    )

