import messages_pb2



f = open('messages.pb', "rb")
address_book.ParseFromString(f.read())
f.close()

ListPeople(address_book)