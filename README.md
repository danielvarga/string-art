# String art

Inspired by https://www.youtube.com/watch?v=ngGIkHFWwHM

Usage:

```python strings.py input-image.png output-prefix```

The input image should be square-shaped.

The output is in ```output-prefix.png```. There are two extra files showing intermediary steps of the computation:
```output-prefix-allow-negative.png``` shows the string art when both black and white strings are allowed.
```output-prefix-unquantized.png``` shows the string art when infinitely thin and long threads are allowed (but only white).

Example output:

Image with allow-negative:

![Trump allow-negative](http://people.mokk.bme.hu/~daniel/trump-h180-r250-q50-c0.3-allow-negative.png)

Image unquantized:

![Trump unquantized](http://people.mokk.bme.hu/~daniel/trump-h180-r250-q50-c0.3-unquantized.png)

Image final, created from ~12000 arcs. Assuming a circle of diameter 1 meter, that's ~10 kilometers of thread:

![Trump final](http://people.mokk.bme.hu/~daniel/trump-h180-r250-q50-c0.3.png)
