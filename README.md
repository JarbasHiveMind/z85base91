

| Encoding    | Avg Encoding Time (ns) | Avg Decoding Time (ns) | Avg Size Increase | Encoding Rank | Decoding Rank | Size Increase Rank |
|-------------|-------------------------|-------------------------|-------------------|---------------|---------------|--------------------|
| [pybase64](https://github.com/mayeut/pybase64)    | 1131 ns                | 2946 ns                | 1.35x            | 1 🥇           | 1 🥇           | 4                  |
| **base91**      | 622324 ns              | 38632 ns               | 1.23x            | 5             | 4             | 1 🥇               |
| [base64](https://docs.python.org/3/library/base64.html)      | 7113 ns                | 7051 ns                | 1.35x            | 3 🥉           | 3 🥉           | 4                  |
| [base16](https://docs.python.org/3/library/binascii.html)      | 5953 ns                | 5859 ns                | 2.00x            | 2 🥈           | 2 🥈           | 6                  |
| **z85b**        | 626214 ns              | 871890 ns              | 1.25x            | 6             | 6             | 2 🥈               |
| **z85p**        | 633825 ns              | 775821 ns              | 1.28x            | 7             | 5             | 3 🥉               |
| [base32](https://docs.python.org/3/library/base64.html)      | 503698 ns              | 882194 ns              | 1.62x            | 4             | 7             | 5                  |
| [z85p_py](https://github.com/JarbasHiveMind/hivemind-websocket-client/blob/dev/hivemind_bus_client/encodings/z85p.py)     | 940859 ns              | 1159043 ns             | 1.28x            | 8             | 8             | 3 🥉               |
| [z85b_py](https://github.com/JarbasHiveMind/hivemind-websocket-client/blob/dev/hivemind_bus_client/encodings/z85b.py)     | 983796 ns              | 1314734 ns             | 1.25x            | 9             | 9             | 2 🥈               |
| [base91_py](https://github.com/JarbasHiveMind/hivemind-websocket-client/blob/dev/hivemind_bus_client/encodings/b91.py)   | 1414374 ns             | 2080957 ns             | 1.23x            | 10            | 10            | 1 🥇               |
