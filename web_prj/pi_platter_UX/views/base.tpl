<!DOCTYPE html>
<html>

<head>
    <title>Pi-Platter - Config</title>
    <link type="text/css" href="main.css" rel="stylesheet">
    <meta charset="UTF-8" name="viewport" content="width=device-width, initial-scale=1">
</head>

<body>
    <div class="site">
        <div class="page-title">
            <h1>Solar Pi-Platter Settings</h1>
        </div>
        <aside class="sidebar">	    
            <a href="/general" {{!'class="active"' if group == 'general' else ""}}>General</a>	    
            <a href="/timers" {{!'class="active"' if group == 'timers' else ""}}>Timers</a>
            <a href="/io" {{!'class="active"' if group == 'io' else ""}}>I/O</a>
            <a href="/control" {{!'class="active"' if group == 'control' else ""}}>Controls</a>
            <a href="/eeprom" {{!'class="active"' if group == 'eeprom' else ""}}>EEPROM</a>
        </aside>
        {{!base}}
        <footer class="footer">
            <p>UX designed by <a href="https://dynamid.citi-lab.fr">CITI Laboratory</a></p>
        </footer>
    </div>
    <!-- .site -->
</body>
<html>
