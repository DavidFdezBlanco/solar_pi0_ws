%# info_table.tpl 
% rebase('base.tpl')
<main class="main-content">
    <div class="table-wrapper">
        <table id="{{group}}">
            <tr>
                <th colspan="3">{{group}}</th>
            </tr>
            %for entry in dict:
            <tr>
                %for item in entry:
                <th id='row_label'>{{item}}</th>
                %if type(entry[item]) == type({'':''}):
                <td id='value'>{{entry[item]['setting']}}</td>
                <td id='control'>
                    <form method="POST" action="/payload">
                        <input type = "hidden" name="page" value="{{group}}">
                        %for button in entry[item]['control']:
                        <button type="submit" name="btn" value="{{entry[item]['control'][button]}}">
                            {{button}}
                        </button>
                        %end
                    </form>
                </td>
                %else:
                <td id='value'>{{entry[item]}}</td>
                %end
                %end
            </tr>
            %end
        </table>
    </div>
</main>
