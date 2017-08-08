from lostservice.logger.transactionaudit import TransactionEvent
from lxml import etree

def create_transaction_log_event(request, data, query_type,start_time, response_text, end_time, conf):
    """
    Create and send the request and response to the transactionlogs
    :param request:
    :param query_type:
    :param start_time:
    :param response_text:
    :param end_time:
    :return:
    """
    trans = TransactionEvent()
    trans.conf = conf
    trans.starttimeutc = start_time
    trans.endtimeutc = end_time
    trans.transactionms = int((start_time-end_time).microseconds)
    trans.response = str(etree.tostring(response_text))
    trans.request = str(etree.tostring(data))


    server_id = response_text.getchildren()[0].attrib.get("source")
    trans.serverid = str(server_id)

    trans.requestsvcurn =  str(data.findtext("service"))
    qname = etree.QName(response_text)
    response_type = "LoST"+str(qname.localname)
    trans.responsetype = response_type

    qname = etree.QName(data)
    request_type = "LoST" + str(qname.localname)
    trans.requesttype = request_type

    requestloc =  etree.tostring(data.getchildren()[0].getchildren()[0])

    trans.requestloc = str(requestloc)
    trans.log()


    return True
