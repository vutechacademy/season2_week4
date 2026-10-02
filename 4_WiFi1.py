from machine import Pin, ADC, time_pulse_us
import network
import socket
import time

# =========================================================
# R-01 WEEK 4
# CONNECT
# ESP32 + Wi-Fi + Network + Web Server
# =========================================================

# -------------------------
# Wi-Fi AP
# -------------------------
AP_SSID = "R-01-AP"
AP_PASSWORD = "12345678"

# -------------------------
# Ultrasonic HC-SR04
# -------------------------
TRIG_PIN = 18
ECHO_PIN = 19

trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

# -------------------------
# LDR
# GPIO34 = ADC Input
# -------------------------
LDR_PIN = 34

ldr = ADC(Pin(LDR_PIN))
ldr.atten(ADC.ATTN_11DB)
ldr.width(ADC.WIDTH_12BIT)

# -------------------------
# OLED I2C
# SDA = GPIO21
# SCL = GPIO22
# -------------------------
OLED_SDA = 21
OLED_SCL = 22

# ถ้ามี SSD1306
try:
    from machine import I2C
    import ssd1306

    i2c = I2C(
        0,
        scl=Pin(OLED_SCL),
        sda=Pin(OLED_SDA),
        freq=400000
    )

    oled = ssd1306.SSD1306_I2C(
        128,
        64,
        i2c
    )

    OLED_OK = True

except Exception as e:
    print("OLED not available:", e)
    OLED_OK = False


# =========================================================
# GLOBAL STATUS
# =========================================================

mode = "READY"
status = "ONLINE"


# =========================================================
# ULTRASONIC
# =========================================================

def read_distance():

    trig.off()
    time.sleep_us(2)

    trig.on()
    time.sleep_us(10)
    trig.off()

    try:
        duration = time_pulse_us(
            echo,
            1,
            30000
        )

        if duration < 0:
            return 0

        distance = (duration * 0.0343) / 2

        return round(distance, 1)

    except:
        return 0


# =========================================================
# LDR
# =========================================================

def read_light():

    value = ldr.read()

    return value


# =========================================================
# OLED
# =========================================================

def show_oled(distance, light):

    if not OLED_OK:
        return

    oled.fill(0)

    oled.text("R-01 STATUS", 0, 0)

    oled.text(
        "DIST : {} cm".format(distance),
        0,
        16
    )

    oled.text(
        "LIGHT: {}".format(light),
        0,
        28
    )

    oled.text(
        "MODE : {}".format(mode),
        0,
        40
    )

    oled.text(
        "STAT : {}".format(status),
        0,
        52
    )

    oled.show()


# =========================================================
# WIFI ACCESS POINT
# =========================================================

def start_wifi():

    ap = network.WLAN(network.AP_IF)

    ap.active(False)
    time.sleep(1)

    ap.active(True)

    ap.config(
        essid=AP_SSID,
        password=AP_PASSWORD,
        authmode=network.AUTH_WPA_WPA2_PSK
    )

    # รอ AP พร้อม
    timeout = 10

    while not ap.active() and timeout > 0:

        print("Starting Wi-Fi...")

        time.sleep(1)

        timeout -= 1

    print()
    print("==============================")
    print("R-01 WEEK 4")
    print("CONNECT")
    print("==============================")
    print("Wi-Fi :", AP_SSID)
    print("IP    :", ap.ifconfig()[0])
    print("==============================")

    return ap


# =========================================================
# WEB PAGE
# =========================================================

def web_page(distance, light):

    html = """<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>R-01 Control</title>

<style>

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #eef5ff;
    color: #102a56;
}

.header {
    background: linear-gradient(
        135deg,
        #0757d5,
        #1595ff
    );

    color: white;

    padding: 22px;

    text-align: center;
}

.header h1 {
    margin: 0;
    font-size: 30px;
}

.header p {
    margin: 5px 0 0;
}

.container {
    max-width: 600px;
    margin: 20px auto;
    padding: 15px;
}

.card {
    background: white;
    border-radius: 18px;
    padding: 20px;
    margin-bottom: 15px;

    box-shadow:
        0 5px 20px rgba(0,0,0,0.10);
}

.title {
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 15px;
}

.row {
    display: flex;
    justify-content: space-between;

    padding: 12px 0;

    border-bottom:
        1px solid #e5e5e5;
}

.label {
    font-weight: bold;
}

.value {
    color: #0757d5;
    font-weight: bold;
}

.online {
    color: #00a651;
}

.footer {
    text-align: center;
    color: #777;
    font-size: 13px;
    margin-top: 20px;
}

.status {
    background: #e8fff1;
    border-radius: 12px;
    padding: 15px;

    text-align: center;

    color: #008a45;

    font-weight: bold;
    font-size: 20px;
}

</style>

<script>

function updateData() {

    fetch('/api')

    .then(response => response.json())

    .then(data => {

        document.getElementById(
            "distance"
        ).innerHTML =
            data.distance + " cm";

        document.getElementById(
            "light"
        ).innerHTML =
            data.light;

        document.getElementById(
            "mode"
        ).innerHTML =
            data.mode;

        document.getElementById(
            "status"
        ).innerHTML =
            data.status;

    });

}

setInterval(updateData, 1000);

</script>

</head>


<body>


<div class="header">

    <h1>R-01 CONTROL</h1>

    <p>VU TECH ACADEMY</p>

</div>


<div class="container">


<div class="card">

    <div class="title">
        DEVICE STATUS
    </div>


    <div class="status">

        NETWORK : ONLINE

    </div>


    <div class="row">

        <span class="label">
            Distance
        </span>

        <span
            class="value"
            id="distance">
            """ + str(distance) + """ cm
        </span>

    </div>


    <div class="row">

        <span class="label">
            Light
        </span>

        <span
            class="value"
            id="light">
            """ + str(light) + """
        </span>

    </div>


    <div class="row">

        <span class="label">
            Mode
        </span>

        <span
            class="value"
            id="mode">
            """ + mode + """
        </span>

    </div>


    <div class="row">

        <span class="label">
            Status
        </span>

        <span
            class="value online"
            id="status">
            """ + status + """
        </span>

    </div>


</div>


<div class="card">

    <div class="title">
        CONNECTION
    </div>

    <div class="row">

        <span class="label">
            Wi-Fi
        </span>

        <span class="value">
            R-01-AP
        </span>

    </div>


    <div class="row">

        <span class="label">
            IP Address
        </span>

        <span class="value">
            192.168.4.1
        </span>

    </div>

</div>


<div class="footer">

    VU TECH ACADEMY<br>

    CONNECTED R-01

</div>


</div>

</body>

</html>
"""

    return html


# =========================================================
# JSON API
# =========================================================

def json_data(distance, light):

    return (
        '{'
        '"distance":' + str(distance) + ','
        '"light":' + str(light) + ','
        '"mode":"' + mode + '",'
        '"status":"' + status + '"'
        '}'
    )


# =========================================================
# START WIFI
# =========================================================

ap = start_wifi()


# =========================================================
# WEB SERVER
# =========================================================

addr = socket.getaddrinfo(
    "0.0.0.0",
    80
)[0][-1]

server = socket.socket()

server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server.bind(addr)

server.listen(1)

print("Web Server Ready")
print("Open Browser:")
print("http://192.168.4.1")


# =========================================================
# MAIN LOOP
# =========================================================

while True:

    distance = read_distance()

    light = read_light()

    show_oled(
        distance,
        light
    )

    try:

        server.settimeout(0.2)

        client, addr = server.accept()

        request = client.recv(1024)

        request = request.decode(
            "utf-8",
            "ignore"
        )

        print("Request:")
        print(request)

        # -----------------------------
        # API
        # -----------------------------

        if "GET /api" in request:

            response = json_data(
                distance,
                light
            )

            client.send(
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/json; charset=UTF-8\r\n"
                "Connection: close\r\n"
                "\r\n"
            )

            client.send(response)

        # -----------------------------
        # Web Page
        # -----------------------------

        else:

            page = web_page(
                distance,
                light
            )

            client.send(
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html; charset=UTF-8\r\n"
                "Connection: close\r\n"
                "\r\n"
            )

            client.send(page)

        client.close()

    except OSError:
        pass

    except Exception as e:

        print("Server Error:", e)

    time.sleep_ms(50)