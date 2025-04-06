curl --location 'http://localhost:5678/webhook-test/' \
--header 'Content-Type: application/json' \
--data '{
  "input_error_text": "psqlexception"
}
'
