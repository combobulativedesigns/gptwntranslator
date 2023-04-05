from yattag import Doc, indent

doc, tag, text = Doc().tagtext()

with tag('root'):
    with tag('doc'):
        with tag('field1', name='blah'):
            text('some value1')
        with tag('field2', name='asdfasd'):
            text('some value2')

result = indent(
    doc.getvalue(),
    indentation = ' '*4,
    newline = '\r\n'
)

print(result)