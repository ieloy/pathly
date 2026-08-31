TODO fixes:
- (BUG) sort_locations geeft momenteel een crash als er nog geen KML-file is geupload, dit crasht dan dus meerdere pagina's - gefixt
- check of sorting.html nu werkt, aangezien ik daar niet de ids meegeef zoals in manual_sorting - gefixt
- model creëren voor user en hier een db aan toevoegen met opgeslagen groepen  - gefixt
- linkje naar de plek waar je die kml file kan maken
- video maken voor common case scenario
- correct routen in elke view, nu kan hij crashen bij een login omdat get_places niks kan returnen (moet eerst naar adminkml) - gefixt
- fixen dat een harde refresh van de page niet ineens opnieuw een form verstuurd en de boel in de war raakt - gefixt


- css fixen (aan het einde)
- mobile usability garanderen (aan het einde)

misschien todo:
- frontend api key maken ipv 1 api key voor alles, nu kunnen mensen in html van routes de api key zien en overnemen
