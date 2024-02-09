# NOTES

### Test Controllers

```
201020304
303986753
405419896
```

```
curl -X POST "http://127.0.0.1:8000/uhppote/simulator/405419896/swipe" -H "accept: application/json" -H "Content-Type: application/json" -d '{"door":1,"card-number":8165535,"direction":1}'

curl -X POST "http://127.0.0.1:8000/uhppote/simulator/405419896/swipe" -H "accept: application/json" -H "Content-Type: application/json" -d '{"door":1,"card-number":8165536,"direction":1}'

curl -X POST "http://127.0.0.1:8000/uhppote/simulator/405419896/door/1" -H "accept: application/json" -H "Content-Type: application/json" -d '{"action":"open"}'

curl -X POST "http://127.0.0.1:8000/uhppote/simulator/405419896/door/1" -H "accept: application/json" -H "Content-Type: application/json" -d '{"action":"close"}'

curl -X POST "http://127.0.0.1:8000/uhppote/simulator/405419896/door/1" -H "accept: application/json" -H "Content-Type: application/json" -d '{"action":"button", "duration":5}'

```

