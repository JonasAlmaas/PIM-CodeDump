#include <Adafruit_NeoPixel.h>

Adafruit_NeoPixel strip;

float GetTimeSeconds()
{
    return (float(millis()) / 1000.0f);
}

namespace Lights
{
    namespace Color
    {
        float idle[3] = {0, 0, 255};
        float pmiShot[3] = {255, 25, 0};
        float success[3] = {0, 255, 0};
        float fail[3] = {255, 0, 0};
    }

    int pin = 9;
    int lightCount = 12;

    float pulsePercent = 0.0f;
    float pulseSpeed = 0.005f;
    bool reversePulse = false;

    bool isLoading = false;
    float timeStartLoading = 0.0f;
    float loadingTime = 1.0f;

    void SetAll(uint16_t r, uint16_t g, uint16_t b)
    {
        for(uint16_t i = 0; i < strip.numPixels(); i++)
        {
            strip.setPixelColor(i, strip.Color(r, g, b));
        }
        strip.show();
    }

    void DisableAll()
    {
        SetAll(0,0,0);
    }

    void Setup()
    {
        strip = Adafruit_NeoPixel(lightCount, pin, NEO_GRB + NEO_KHZ800);
        strip.begin();
        DisableAll();
    }

    void Blink(int repeat, float timeDelay, uint16_t r, uint16_t g, uint16_t b)
    {
        for (uint16_t i = 0; i < repeat; i++)
        {
            SetAll(r, g, b);
            delay(timeDelay);
            DisableAll();
            delay(timeDelay);
        }
    }

    void Progress(float duration, int r, int g, int b)
    {
        DisableAll();

        float startTime = GetTimeSeconds();
        float timePassed = 0.0f;

        while (timePassed < duration)
        {
            timePassed = GetTimeSeconds() - startTime;
            float percent = timePassed / duration;

            for (uint16_t i = 0; i < int(Lights::lightCount * (percent + 0.05f)); i++)
            {
                strip.setPixelColor(i, strip.Color(r, g, b));
            }
            strip.show();
            delay(50);
        }
    }

    void ResetIdle()
    {
        reversePulse = false;
        pulsePercent = 0.0;
    }

    void ThinkIdle()
    {
        if (reversePulse) { pulsePercent -= pulseSpeed; }
        else { pulsePercent += pulseSpeed; }

        if (pulsePercent < 0.0f)
        {
            pulsePercent = 0.0f;
            reversePulse = false;
        }
        else if (pulsePercent > 1.0f)
        {
            pulsePercent = 1.0f;
            reversePulse = true;
        }

        SetAll(int(Color::idle[0] * pulsePercent), int(Color::idle[1] * pulsePercent), int(Color::idle[2] * pulsePercent));
    }

    void ThinkLoading(float duration, int r, int g, int b)
    {
        DisableAll();
        float currentTime = GetTimeSeconds();
        float timePassed = currentTime - timeStartLoading;

        float percent = timePassed / duration;
        if (percent > 1.0)
        {
            percent = 1;
            timeStartLoading = GetTimeSeconds();
        }

        strip.setPixelColor(int(Lights::lightCount * percent), strip.Color(r, g, b));
        strip.show();
    }
}

namespace Actuator
{
    int pinOpen = 7;
    int pinClose = 8;

    void Setup()
    {
        pinMode(pinOpen, OUTPUT);
        pinMode(pinClose, OUTPUT);

        digitalWrite(pinOpen, false);
        digitalWrite(pinClose, false);
    }
    
    void Activate()
    {
        digitalWrite(pinClose, false);
        delay(20);
        digitalWrite(pinOpen, true);
    }

    void Deactivate()
    {
        digitalWrite(pinOpen, false);
        delay(20);
        digitalWrite(pinClose, true);
    }
}

namespace PMI
{
    float ShootingTime = 10.0f;

    void StartShooting()
    {
        Actuator::Activate();
        Lights::Progress(ShootingTime, Lights::Color::pmiShot[0], Lights::Color::pmiShot[1], Lights::Color::pmiShot[2]);
        Actuator::Deactivate();
        Lights::Blink(5, 75, Lights::Color::pmiShot[0], Lights::Color::pmiShot[1], Lights::Color::pmiShot[2]);
    }
}

void setup()
{
    Serial.begin(115200);
    Serial.setTimeout(1);

    Lights::Setup();
    Actuator::Setup();
}

void loop()
{
    if (Serial.available() > 0)
    {
        int data = Serial.readString().toInt();
        
        switch (data)
        {
            // General Flash
            case 1: { Lights::Blink(5, 75, Lights::Color::idle[0], Lights::Color::idle[1], Lights::Color::idle[2]); break; }
            // Start Loading
            case 2: { Lights::isLoading = true; break; }
            // Stop Loading
            case 3: { Lights::isLoading = false; break; }
            // PMI Start Shooting
            case 4: { PMI::StartShooting(); break; }
            // PMI Success
            case 5: { Lights::Blink(5, 75, Lights::Color::success[0], Lights::Color::success[1], Lights::Color::success[2]); break; }
            // PMI Fail
            case 6: { Lights::Blink(5, 75, Lights::Color::fail[0], Lights::Color::fail[1], Lights::Color::fail[2]); break; }
            default: { break; }
        }
        Lights::ResetIdle();
    }

    if (Lights::isLoading)
    {
        Lights::ThinkLoading(Lights::loadingTime, Lights::Color::idle[0], Lights::Color::idle[1], Lights::Color::idle[2]);
    }
    else {
        Lights::ThinkIdle();
    }
    delay(10);
}
